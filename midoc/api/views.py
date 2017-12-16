import culqipy
import json
import sys
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, Http404
from django.db import transaction
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from .utils import calculate_age, validate_one_character, getAuthTicket, code_generator
from .tasks import personal_plan, welcome, recovery
from .serializers import (DoctorSerializer,
                          EnterpriseSerializer,
                          DoctorLocalSerializer,
                          MedicalHistorySerializer,
                          PatientSerializer,
                          PatientVerifySerializer,
                          ArtifactMeasurementSerializer,
                          RecoveryEmailSerializer,
    # PatientHistorySerializer
                          PatientUpdatingSerializer,
                          CompetitionSerializer,
                          PatientSerializer2,
                          MedicalHistorySerializer2,
                          VoucherSerializer,
                          CardInfoSerializer,
                          CustomerPaymentInfoSerializer,
                          )
from .models import (Doctor,
                     Location,
                     Enterprise,
                     EmergencyAttention,
                     LocationEmergencyAttention,
                     MedicalHistory,
                     Patient,
                     MedicalHistoryMedia,
                     Appointment,
                     ArtifactMeasurement,
                     Competition,
                     Voucher,
                     Plan,
                     Plantype,
                     PaymentTransaction,
                     RecoveryEmail,

                     )


# clinic check
# class PatientRegisterView(APIView):
#     serializer_class = PatientSerializer
#
#     def get(self, format=None):
#         serializer = self.serializer_class(Patient.objects.all(), many=True)
#         print(serializer.data)
#         return Response(serializer.data)
#
#     def post(self, request, format=None):
#         serializer = self.serializer_class(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



        # def post(self, request, format=None):
        #     serializer = self.serializer_class(data=request.data)
        #     serializer.is_valid(raise_exception=True)
        #     serializer.save()
        #
        #     response_msg = {'details': "El paciente fue registrato satisfactoriamente",
        #                     "status": status.HTTP_200_OK}
        #     return Response(response_msg)


# clinic check
class DoctorListView(APIView):
    serializer_class = DoctorSerializer

    def get(self, request, format=None):
        doctor = Doctor.objects.all().order_by('call_activate')
        serializer = DoctorSerializer(doctor, many=True)
        clinics = {"asesores": serializer.data}
        return Response(clinics)


# clinic check
class DoctorUpdateAttention(APIView):
    """
    Retrieve, update a Doctor instance.
    """

    def get_object(self, pk):
        try:
            return Doctor.objects.get(pk=pk)
        except Doctor.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        doctor = self.get_object(pk)
        serializer = DoctorSerializer(doctor)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        doctor = self.get_object(pk)
        serializer = DoctorSerializer(doctor, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# clinic check
class CompetitionView(APIView):
    serializer_class = CompetitionSerializer

    def get(self, request, format=None):
        serializer = self.serializer_class(Competition.objects.all(), many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        # serializer.is_valid(raise_exception=True)
        try:
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                print(serializer.errors)
                return Response({"message": "403 Forbidden"},
                                status=status.HTTP_409_CONFLICT)
        except Exception as inst:
            print('Caught this error: ' + repr(inst))


# check clinic
class DoctorLogin(APIView):
    serializer_class = DoctorSerializer

    def get(self, request, format=None):
        doctor = Doctor.objects.all()
        serializer = DoctorSerializer(doctor, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data

        print(vd)
        print(vd.get("midoc_user"))
        print(vd.get("password"))
        try:
            if Doctor.objects.filter(
                    midoc_user__exact=vd.get("midoc_user")).exists() \
                    and Doctor.objects.filter(
                        password__exact=vd.get("password")).exists():
                doctor = Doctor.objects.get(midoc_user=vd.get("midoc_user"))
                print(doctor.pk)
                print(doctor.doctor_name)
                print(doctor.midoc_user)
                print(doctor.password)

                user = {'username': vd.get("midoc_user")}

                ticket = getAuthTicket(user)

                print(doctor.location_id)
                location = Location.objects.get(pk=doctor.location_id)
                # location.enterprise.picture_url_enterprise

                d = {"id": doctor.pk, "cmd_peru": doctor.cmd_peru,
                     "degree": doctor.degree, "doctor_name": doctor.doctor_name,
                     "year_of_birth": doctor.year_of_birth,
                     "picture_url": doctor.picture_url,
                     "location_id": doctor.location_id,
                     "email": doctor.email, "midoc_user": doctor.midoc_user,
                     "password": doctor.password,
                     "type_of_specialist": doctor.type_of_specialist,
                     "is_enabled": doctor.is_enabled,
                     "picture_url_enterprise": location.enterprise.picture_url_enterprise,
                     "ticket": ticket,
                     "call_activate": doctor.call_activate}
                print(d)
                return Response(d)
                # return HttpResponse(json.dumps(d, cls=DjangoJSONEncoder), content_type='application/json')
            else:
                print(">>> no hay!")
                response_msg = {'details': 'El usuario no existe',
                                'status': status.HTTP_409_CONFLICT}
                print(response_msg)
                return HttpResponse(
                    json.dumps(response_msg, cls=DjangoJSONEncoder),
                    content_type='application/json')

        except Exception as inst:
            print(inst)
            print(">>> exception block")
            response_msg = {'details': 'User exception',
                            'status': status.HTTP_409_CONFLICT,
                            "exception": inst}
            print(response_msg)
            return HttpResponse(json.dumps(response_msg, cls=DjangoJSONEncoder),
                                content_type='application/json')


# ckeck clinic
class PatientUpdateToken(APIView):
    """
    Retrieve, update a Patient instance.
    """

    def get_object(self, pk):
        try:
            return Patient.objects.get(pk=pk)
        except Patient.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        patient = self.get_object(pk)
        serializer = PatientSerializer(patient)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        patient = self.get_object(pk)
        serializer = PatientSerializer(patient, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# check token clinic
class PatientByTokenList(APIView):
    # renderer_classes = (JSONRenderer,)
    def get(request, *args, **kwargs):
        token_sinch = kwargs['token_sinch']
        print(token_sinch)
        is_token_sinch = Patient.objects.filter(
            token_sinch__exact=token_sinch).exists()
        print(is_token_sinch)
        if is_token_sinch:
            patient_list = Patient.objects.filter(
                token_sinch__exact=token_sinch)
            print(patient_list)
            patient_dict = [{"id": patient.pk, "name": patient.name,
                             "age": calculate_age(patient.year_of_birth),
                             "email": patient.email,
                             "password": patient.password, "dni": patient.dni,
                             "picture_url": patient.picture_url,
                             "blood_type": patient.blood_type,
                             "allergic_reaction": patient.allergic_reaction,
                             "token_sinch": patient.token_sinch,
                             "size": patient.size, "gender": patient.gender,
                             "contact_phone": patient.contact_phone,
                             "is_enterprise_enabled": patient.is_enterprise_enabled
                             # "enterprise_name": patient.location.enterprise.en
                             } for patient in patient_list
                            ]
            return Response(patient_dict)
        else:
            response_msg = [
                {'warning': 'This token not exist:%s' % token_sinch}]
            return Response(response_msg)


# check clinic nested clinic medical history
# dev child json update/create
class PatientMedicalHistory(APIView):
    serializer_class = PatientSerializer2

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # vd = serializer.validated_data

        response_msg = {'details': 'La Historia medica fue insertada',
                        'status': status.HTTP_201_CREATED}
        print(response_msg)
        return HttpResponse(json.dumps(response_msg, cls=DjangoJSONEncoder),
                            content_type='application/json')

        # return Response("Fisnish POST response")

    def put(self, request, format=None):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            patient_id = request.data['id']
            print(patient_id)
            patient = Patient.objects.get(pk=patient_id)
            serializer.update(patient, request.data)

            # vd = serializer.validated_data

            response_msg = {'details': 'La historia medica fue actualizada',
                            'status': status.HTTP_200_OK}
            print(response_msg)
            return HttpResponse(json.dumps(response_msg, cls=DjangoJSONEncoder),
                                content_type='application/json')
        except Exception as inst:
            print(inst)
            response_msg = {'details': inst, 'status': status.HTTP_409_CONFLICT}
            print(response_msg)
            return HttpResponse(json.dumps(response_msg, cls=DjangoJSONEncoder),
                                content_type='application/json')

            # return Response("Fisnish PUT response")


# clinic Doctor Attention
# select * from patient where id in (
# select DISTINCT(patient_id) from medical_history where doctor_id = 1);
class DoctorAttentionPatient2(APIView):
    def get(self, request, *args, **kwargs):
        doctor_id = kwargs["doctor_id"]
        if doctor_id:
            mhs = MedicalHistory.objects.filter(
                doctor_id=doctor_id).values_list('patient_id',
                                                 flat=True).distinct(
                'patient_id')
            patient_list = []
            for mh in mhs:
                patient = Patient.objects.get(pk=mh)
                patient_list.append(patient)
                # print(patient_list)
            patient_dict2 = [{"id": patient.pk, "name": patient.name,
                              "age": calculate_age(patient.year_of_birth),
                              "email": patient.email,
                              "password": patient.password, "dni": patient.dni,
                              "picture_url": patient.picture_url,
                              "blood_type": patient.blood_type,
                              "allergic_reaction": patient.allergic_reaction,
                              "token_sinch": patient.token_sinch,
                              "size": patient.size, "gender": patient.gender,
                              "contact_phone": patient.contact_phone,
                              "is_enterprise_enabled": patient.is_enterprise_enabled
                              } for patient in patient_list]
            return Response(patient_dict2)


class DoctorAttentionPatient(APIView):
    def get(self, request, *args, **kwargs):
        doctor_id = kwargs["doctor_id"]
        if doctor_id:
            mhs = MedicalHistory.objects.filter(doctor_id=doctor_id).order_by(
                '-created_date')
            print(mhs.count())
            patient_list = []
            for mh in mhs:
                patient = Patient.objects.get(pk=mh.patient.pk)
                patient_list.append(patient)
                # print(patient_list)
            patient_dict2 = [
                {"id": patient.pk, "name": patient.name,
                 "age": calculate_age(patient.year_of_birth),
                 "email": patient.email, "password": patient.password,
                 "dni": patient.dni,
                 "picture_url": patient.picture_url,
                 "blood_type": patient.blood_type,
                 "allergic_reaction": patient.allergic_reaction,
                 "token_sinch": patient.token_sinch,
                 "size": patient.size, "gender": patient.gender,
                 "contact_phone": patient.contact_phone,
                 "is_enterprise_enabled": patient.is_enterprise_enabled,
                 "created_date": patient.created_date
                 } for patient in patient_list]
            return Response(patient_dict2)


# clinic
class MedicalHistoryByPatient(APIView):
    def get(self, request, *args, **kwargs):
        patient_id = kwargs["patient_id"]
        if patient_id:
            mhs = MedicalHistory.objects.filter(patient_id=patient_id).order_by(
                '-created_date')
            medical_history = [{"id": mh.pk, "location_id": mh.location_id,
                                "medical_history_text": mh.medical_history_text,
                                "symptom": mh.symptom,
                                "doctor_comment": mh.doctor_comment,
                                "diagnostic": mh.diagnostic,
                                "weight": mh.weight,
                                "body_temperature": mh.body_temperature,
                                "blood_pressure": mh.blood_pressure,
                                "heart_rate": mh.heart_rate,
                                "next_medical_date": mh.next_medical_date,
                                "created_date": mh.created_date} for mh in mhs]
            medical_history_list = {"medical_history": medical_history}
            return Response(medical_history_list)
        else:
            response_msg = {
                "details": "Este Patiente no existe o no fue aun registrado",
                "status": status.HTTP_409_CONFLICT}
            print(response_msg)
            return HttpResponse(json.dumps(response_msg, cls=DjangoJSONEncoder),
                                content_type='application/json')


# clinic
class BusinessActivationCode(APIView):
    # serializer_class = VoucherSerializer

    """
    Retrieve, update a Voucher instance.
    """

    def get_object(self, code):
        try:
            return Voucher.objects.get(code=code)
        except Voucher.DoesNotExist:
            raise Http404

    def get(self, request, code, format=None):
        voucher = self.get_object(code)
        serializer = VoucherSerializer(voucher)
        return Response(serializer.data)

    # def put(self, request, coupon, format=None):
    #     voucher = self.get_object(coupon)
    #     serializer = VoucherSerializer(voucher, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        serializer = VoucherSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data
        code = kwargs["code"]
        print(code)
        print(vd.get("state"))
        print(vd.get("device_id"))
        try:
            if Voucher.objects.filter(code__iexact=code).exists():
                # recovery the patient
                voucher = Voucher.objects.get(code__exact=code)
                if voucher.state == '0':
                    voucher.state = '1'
                    voucher.device_id = vd.get("device_id")
                    voucher.save()

                elif voucher.state == '1' and voucher.device_id == vd.get(
                        "device_id"):
                    response_msg = {'details': 'Bienvenido de vuelta',
                                    'status': status.HTTP_200_OK}
                    return HttpResponse(
                        json.dumps(response_msg, cls=DjangoJSONEncoder),
                        content_type='application/json')
                elif voucher.state == '1' and voucher.device_id != vd.get(
                        "device_id"):
                    response_msg = {
                        'details': 'El código esta siendo usado, por favor intenta con un nuevo código',
                        'status': status.HTTP_404_NOT_FOUND}
                    return HttpResponse(
                        json.dumps(response_msg, cls=DjangoJSONEncoder),
                        content_type='application/json')
                elif voucher.state == '2':
                    response_msg = {'details': 'Este código ya expiró',
                                    'status': status.HTTP_404_NOT_FOUND}
                    return HttpResponse(
                        json.dumps(response_msg, cls=DjangoJSONEncoder),
                        content_type='application/json')

                # p = {"id": patient.pk, "name": patient.name, "email": patient.email,
                #      "password": patient.password, "dni": patient.dni, "picture_url": patient.picture_url,
                #      "enterprise_enabled": patient.is_enterprise_enabled, "blood_type": patient.blood_type,
                #      "allergic_reaction": patient.allergic_reaction, "token_sinch": patient.token_sinch,
                #      "size": patient.size
                # }

                v = {"id": voucher.pk, "name": voucher.name,
                     "code": voucher.code, "usage": voucher.usage,
                     "state": voucher.state, "device_id": voucher.device_id
                     }

                return Response(v)
            else:
                response_msg = {'details': 'El voucher no existe',
                                'status': status.HTTP_404_NOT_FOUND}
                return HttpResponse(
                    json.dumps(response_msg, cls=DjangoJSONEncoder),
                    content_type='application/json')

        except Exception as inst:
            print(">>> create failure")
            print(inst)
            response_msg = [{'create': 'failure'}]
            return HttpResponse(json.dumps(response_msg, cls=DjangoJSONEncoder),
                                content_type='application/json')


# end clinic API
# ==============


# Headquarters list by enterprise.
class EnterpriseHeadquarters(APIView):
    def get(self, request, *args, **Kwargs):
        enterprise_id = Kwargs["enterprise_id"]
        print(enterprise_id)
        if enterprise_id:
            enterprise = Enterprise.objects.get(pk=enterprise_id)
            location_list = Location.objects.filter(enterprise=enterprise_id)
            location_array = [{"id": location.pk, "name": location.name,
                               "description": location.description} for
                              location in location_list]
            location = {"location": location_array}
            return Response(location)
        else:
            response_msg = [
                {'warning': 'This location does not exist %s' % enterprise_id}]
            return Response(response_msg)


# check,
class ClinicsList(APIView):
    serializer_class = EnterpriseSerializer

    def get(self, reques, format=None):
        enterprise = self.serializer_class(Enterprise.objects.all(), many=True)
        clinics = {"enterprise": enterprise.data}
        return Response(clinics)


# check
# select ap.* from emergency_attention ap
# INNER JOIN location_emergency_attention lea  on ap.id = lea.emergency_attention_id
# where lea.location_id = 1;
# select_related review
class EmergencyAttentionList(APIView):
    # get the location = id
    def get(self, request, *args, **kwargs):
        location_emergency_attention_list = LocationEmergencyAttention.objects.filter(
            location_id=self.kwargs['location_id'])
        print(location_emergency_attention_list.count())

        emergency_attention_id_list = [
            location_emergency_attention.emergency_attention_id
            for location_emergency_attention in
            location_emergency_attention_list]
        print(emergency_attention_id_list)

        emergency_attention_list = [
            EmergencyAttention.objects.get(pk=emergency_attention_id)
            for emergency_attention_id in emergency_attention_id_list]
        print(emergency_attention_list)
        dict = [{"id": emergency_attention.id,
                 "name": emergency_attention.attention_type_id,
                 "description": emergency_attention.description,
                 "picture_url": emergency_attention.picture_url}
                for emergency_attention in emergency_attention_list]

        emergency_attention = {"emergency_attention": dict}

        return Response(emergency_attention)


# check
# Specialist Doctor by location
class SpecialistDoctor(APIView):
    def get(self, *args, **kwargs):
        type_of_specialist = "ESPEC"
        doctor_list = Doctor.objects.filter(
            location_id=self.kwargs['location_id']) \
            .filter(type_of_specialist=type_of_specialist) \
            .filter(
            emergency_attention_id__exact=self.kwargs['emergency_attention_id'])
        doctor = [{"id": doctor.pk, "doctor_name": doctor.doctor_name,
                   "email": doctor.email, "midoc_user": doctor.midoc_user,
                   "picture_url": doctor.picture_url} for doctor in doctor_list]
        payload = {"specialist_doctor": doctor}
        return Response(payload)


# check
# emergency doctor by location
class EmergencyDoctor(APIView):
    serializer_class = DoctorLocalSerializer

    def get(self, request, *args, **kwargs):
        type_of_specialist = "EMERG"
        doctor_list = Doctor.objects.filter(
            location_id=self.kwargs['location_id']). \
            filter(type_of_specialist=type_of_specialist)
        doctor = [{"id": doctor.pk, "doctor_name": doctor.doctor_name,
                   "picture_url": doctor.picture_url,
                   "cmd": doctor.cmd_peru} for doctor in doctor_list]
        clinics = {"emergency_doctor": doctor}
        return Response(clinics)


# check
# select mh.id as medical_history_id, p.name, p.year_of_birth, p.blood_type, p.allergic_reaction
# from medical_history mh inner join patient p on (mh.patient_id = p.id)
# where mh.emergencista_id = 5 and mh.location_id =1 and mh.doctor_id =2;
class MedicalHistoryList(APIView):
    serializer_class = MedicalHistorySerializer

    def get(self, request, *args, **kwargs):
        doctor_id = self.kwargs['doctor_id']
        location_id = self.kwargs['location_id']
        emergency_doctor_id = self.kwargs['emergency_doctor_id']
        print(doctor_id)
        print(location_id)
        print(emergency_doctor_id)

        medical_history_list = MedicalHistory.objects.filter(
            location_id=self.kwargs['location_id']) \
            .filter(doctor=doctor_id).filter(
            emergencista=emergency_doctor_id).order_by('created_date')
        print(medical_history_list)

        medical_history_dict = [{"patient_id": medical_history.patient.pk,
                                 "medical_history_id": medical_history.id,
                                 "age": calculate_age(
                                     medical_history.patient.year_of_birth),
                                 "fecha_ingreso": medical_history.created_date,
                                 "name": medical_history.patient.name} for
                                medical_history in medical_history_list]
        dict = {"emergency_patient": medical_history_dict}
        return Response(dict)


# check
class MedicalHistoryListByEmergDoctor(APIView):
    serializer_class = MedicalHistorySerializer

    def get(self, request, *args, **kwargs):
        emergency_doctor_id = self.kwargs['emergency_doctor_id']
        location_id = self.kwargs['location_id']

        print(location_id)
        print(emergency_doctor_id)

        medical_history_list = MedicalHistory.objects.filter(
            location_id=self.kwargs['location_id']).filter(
            emergencista=emergency_doctor_id).order_by('created_date')
        print(medical_history_list)

        medical_history_dict = [{"patient_name": mh.patient.name,
                                 "doctor_name": mh.emergencista.doctor_name,
                                 "attention_name": mh.doctor.emergency_attention.attention_name,
                                 "created_date": mh.created_date,
                                 "picture_url": mh.patient.picture_url,
                                 "id": mh.pk,
                                 } for mh in medical_history_list]
        dict = {"emergency_history": medical_history_dict}
        return Response(dict)


# dev
class MedicalHistorySpecialistList(APIView):
    serializer_class = MedicalHistorySerializer

    def get(self, request, *args, **kwargs):
        doctor_id = self.kwargs['doctor_id']
        location_id = self.kwargs['location_id']
        # specialist_doctor_id = self.kwargs['specialist_doctor_id']
        print(doctor_id)
        print(location_id)
        # print(specialist_doctor_id)

        medical_history_list = MedicalHistory.objects.filter(
            location_id=self.kwargs['location_id']). \
            filter(doctor=doctor_id).order_by('created_date')
        print(medical_history_list)

        medical_history_dict = [{"patient_id": medical_history.patient.pk,
                                 "medical_history_id": medical_history.id,
                                 "age": calculate_age(
                                     medical_history.patient.year_of_birth),
                                 "fecha_ingreso": medical_history.created_date,
                                 "specialty_name": medical_history.doctor.emergency_attention.attention_name,
                                 "emergency_name": medical_history.emergencista.doctor_name,
                                 "name": medical_history.patient.name} for
                                medical_history in medical_history_list]
        dict = {"emergency_patient": medical_history_dict}
        return Response(dict)


# check
class MedicalHistoryDetail(APIView):
    def get(self, request, *args, **kwargs):
        medical_history_id = self.kwargs['medical_history_id']
        mh = MedicalHistory.objects.get(pk=medical_history_id)

        patient = {"name": mh.patient.name,
                   "edad": calculate_age(mh.patient.year_of_birth),
                   "tipo_de_sangre": mh.patient.blood_type,
                   "alergias": mh.patient.allergic_reaction,
                   "contact_phone": mh.patient.contact_phone,
                   "created_date": mh.patient.created_date,
                   "gender": mh.patient.gender, "diagnostic": mh.diagnostic,
                   "symptom": mh.symptom, "blood_type": mh.patient.blood_type,
                   "size": mh.patient.size, "email": mh.patient.email,
                   "picture_url": mh.patient.picture_url, "dni": mh.patient.dni}

        emergencista = {"nombre_emergencista": mh.emergencista.doctor_name,
                        "emergencista_sintoma": mh.symptom,
                        "doctor_foto": mh.emergencista.picture_url,
                        "cmd": mh.emergencista.cmd_peru}

        doctor = {"especialista_name": mh.doctor.doctor_name,
                  "doctor_foto": mh.doctor.picture_url,
                  "cmd": mh.doctor.cmd_peru,
                  "especialista_comment": mh.doctor_comment}

        # get the picture medical history detail
        mhm_list = MedicalHistoryMedia.objects.filter(
            medical_history=medical_history_id)

        mhm2 = [{"picture_patient": mhm.picture_url} for mhm in mhm_list]

        # headers for medical history detail
        headers = {"picture_detail": "Fotos", "emergencista": "Médico de Área",
                   "patient": "Paciente", "doctor": "Especialista"}

        medical_history_detail = [
            {"patient": patient, "emergencista": emergencista, "doctor": doctor,
             "picture_detail": mhm2, "headers": headers}]
        print(medical_history_detail)

        dict = {"medical_history_detail": medical_history_detail}

        return Response(dict)


# dev child json update/create
class MedicalHistoryUpdating(APIView):
    serializer_class = PatientUpdatingSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # vd = serializer.validated_data


        return Response("hola")


"""
deprecated
"""


class PatientViewDeprecated(APIView):
    serializer_class = PatientSerializer

    def get(self, format=None):
        serializer = self.serializer_class(Patient.objects.all(), many=True)
        return Response(serializer.data)

    @transaction.atomic()
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data
        print(vd.get("dni"))
        try:
            if not Patient.objects.filter(dni__exact=vd.get("dni")).exists():
                print("object to save: {}".format(vd))
                # save and get the recent id
                patient = serializer.save()
                print(patient.dni)
                # patient.pk get the recent id

                p = {"id": patient.pk, "name": patient.name,
                     "email": patient.email,
                     "password": patient.password, "dni": patient.dni,
                     "picture_url": patient.picture_url,
                     "enterprise_enabled": patient.is_enterprise_enabled,
                     "blood_type": patient.blood_type,
                     "allergic_reaction": patient.allergic_reaction,
                     "token_sinch": patient.token_sinch,
                     "nokia_weight": patient.nokia_weight,
                     "nokia_body_temperature": patient.nokia_body_temperature,
                     "nokia_blood_pressure": patient.nokia_blood_pressure,
                     "size": patient.size,
                     "is_enterprise_enabled": patient.is_enterprise_enabled
                     }

                print(p)
                # return HttpResponse(json.dumps(p, cls=DjangoJSONEncoder), content_type='application/json')
                return Response(p)


            else:
                print(">>> Usuario ya se encuentra registrado")
                response_msg = {'details': 'Este Usuario ya esta registrado',
                                'status': status.HTTP_409_CONFLICT}
                return HttpResponse(
                    json.dumps(response_msg, cls=DjangoJSONEncoder),
                    content_type='application/json')
        except:
            print(">>> create failure")
            responseMsg = [{'create': 'failure'}]
            return HttpResponse(json.dumps(responseMsg, cls=DjangoJSONEncoder),
                                content_type='application/json')


# check
class PatientView(APIView):
    serializer_class = PatientSerializer

    def get(self, format=None):
        serializer = self.serializer_class(Patient.objects.all(), many=True)
        return Response(serializer.data)

    @transaction.atomic()
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data
        print(vd.get("dni"))
        try:
            if Patient.objects.filter(dni__iexact=vd.get("dni")).exists():
                # recovery the patient
                patient = Patient.objects.get(dni__iexact=vd.get("dni"))

                p = {"id": patient.pk, "name": patient.name,
                     "email": patient.email,
                     "password": patient.password, "dni": patient.dni,
                     "picture_url": patient.picture_url,
                     "enterprise_enabled": patient.is_enterprise_enabled,
                     "blood_type": patient.blood_type,
                     "allergic_reaction": patient.allergic_reaction,
                     "token_sinch": patient.token_sinch,
                     "size": patient.size
                     }

                return Response(p)
            else:
                response_msg = {
                    'details': 'Este Paciente no se encuentra registrado',
                    'status': status.HTTP_404_NOT_FOUND}
                return HttpResponse(
                    json.dumps(response_msg, cls=DjangoJSONEncoder),
                    content_type='application/json')

        except Exception as inst:
            print(">>> create failure")
            print(inst)
            response_msg = [{'create': 'failure'}]
            return HttpResponse(json.dumps(response_msg, cls=DjangoJSONEncoder),
                                content_type='application/json')


# check
# class PatientRegisterView(APIView):
#     serializer_class = PatientSerializer
#
#     def get(self, format=None):
#         serializer = self.serializer_class(Patient.objects.all(), many=True)
#         return Response(serializer.data)
#
#     #@transaction.atomic()
#     def post(self, request, format=None):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         vd = serializer.validated_data
#         print(vd.get("dni"))
#         try:
#             if not Patient.objects.filter(dni__exact=vd.get("dni")).exists():
#                 print("object to save: {}".format(vd))
#                 # save and get the recent id
#                 patient = serializer.save()
#                 print(patient.dni)
#                 # patient.pk get the recent id
#
#                 p = {"id": patient.pk, "name": patient.name, "email": patient.email,
#                      "password": patient.password, "dni": patient.dni, "picture_url": patient.picture_url,
#                      "enterprise_enabled": patient.is_enterprise_enabled, "blood_type": patient.blood_type,
#                      "allergic_reaction": patient.allergic_reaction, "token_sinch": patient.token_sinch,
#                      "size": patient.size, "is_enterprise_enabled": patient.is_enterprise_enabled
#                      }
#                 print(p)
#                 # return HttpResponse(json.dumps(p, cls=DjangoJSONEncoder), content_type='application/json')
#                 return Response(p)
#
#             else:
#                 print(">>> Usuario ya se encuentra registrado")
#                 response_msg = {'details': 'Este Usuario ya esta registrado', 'status': status.HTTP_409_CONFLICT}
#                 return HttpResponse(json.dumps(response_msg, cls=DjangoJSONEncoder), content_type='application/json')
#
#         except Exception as inst:
#             print(">>> create failure")
#             print(inst)
#             response_msg = [{'create': 'failure'}]
#             return HttpResponse(json.dumps(response_msg, cls=DjangoJSONEncoder), content_type='application/json')




# developer status
class DoctorUpdateLocationView(APIView):
    def put(self, request, *args, **kwargs):
        data = request.data
        # print(data)
        location_id2 = kwargs['location_id']
        print(location_id2)
        doctor_id = kwargs['doctor_id']
        print(doctor_id)
        try:
            doctor = Doctor.objects.filter(pk=doctor_id).update(
                location_id=location_id2)
            print(doctor)
            d = Doctor.objects.get(pk=doctor_id)
            new_location = d.location_id

            if doctor == 1:
                response_msg = {'id': new_location,
                                'details': "La sede del doctor fue actualizada",
                                "status": status.HTTP_200_OK}
                return Response(response_msg)

            else:
                response_msg = {
                    'details': "La sede del doctor NO fue actualizada",
                    "status": status.HTTP_403_FORBIDDEN}
                return Response(response_msg)

        except Exception as inst:
            print(inst)
            response_msg = {'details': "El doctor no existe!",
                            "status": status.HTTP_404_NOT_FOUND}
            return Response(response_msg)


# developer status
class MedicalHistoryUpdate(APIView):
    """
    Retrieve, update a Medical History instance.
    """

    def get_object(self, pk):
        try:
            return MedicalHistory.objects.get(pk=pk)
        except MedicalHistory.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        medical_history = self.get_object(pk)
        serializer = MedicalHistorySerializer(medical_history)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        medical_history = self.get_object(pk)
        serializer = MedicalHistorySerializer(medical_history,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# check
class PatientVerifyView(APIView):
    serializer_class = PatientVerifySerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data
        print(vd.get("dni"))
        print(vd.get("enterprise_id"))

        try:
            patient = Patient.objects.get(dni__exact=vd.get("dni"))
        except Patient.DoesNotExist:
            patient = None

        if patient is None:
            response_msg = {'details': "El Paciente no se encuentra registrado",
                            "status": status.HTTP_403_FORBIDDEN}
            return Response(response_msg)

        try:
            enterprise = Enterprise.objects.get(pk=vd.get("enterprise_id"))
        except Enterprise.DoesNotExist:
            enterprise = None

        if enterprise is None:
            response_msg = {
                'details': "La empresa que requieres aun no ha sido registrada",
                "status": status.HTTP_403_FORBIDDEN}
            return Response(response_msg)

        else:
            # location = Location.objects.get(pk=patient.location.pk)
            # print(location.enterprise_id)
            print(enterprise.business_name)

            dict = {"patient_id": patient.pk, "dni": patient.dni,
                    "name": patient.name, "midoc_user": patient.midoc_user,
                    "business_name": enterprise.business_name,
                    "picture_url": patient.picture_url,
                    "picture_url_enterprise": enterprise.picture_url_enterprise}

            return Response(dict)


# check
class PatientAppointments(APIView):
    def get(request, *args, **kwargs):
        patient_id = kwargs['patient_id']

        appointments = Appointment.objects.filter(patient_id=patient_id)

        appointment_dict = [{"appointment_id": appointment.pk,
                             "doctor_name": appointment.doctor.doctor_name,
                             "appointment_time": appointment.appointment_time,
                             "specialty:": appointment.doctor.
                                 emergency_attention.attention_name,
                             "appointment_status":
                                 appointment.appointment_status} for appointment
                            in appointments]

        dict = {"appoitment_patient": appointment_dict}

        return Response(dict)


# dev status
class PatientHistoryView(APIView):
    def get(request, *args, **kwargs):
        patient_id = kwargs['patient_id']

        medicalhistorys = MedicalHistory.objects.filter(patient_id=patient_id)

        medical = [{"age": calculate_age(medicalhistory.patient.year_of_birth),
                    "patient_id": medicalhistory.patient.pk,
                    "fecha_ingreso": medicalhistory.patient.created_date,
                    "name": medicalhistory.doctor.doctor_name,
                    "medical_history_id": medicalhistory.pk,
                    "specialty_name": medicalhistory.doctor.emergency_attention.attention_name}
                   for medicalhistory in medicalhistorys]

        dict = {"patient_history": medical}

        return Response(dict)


# dev artifact
class ArtifactMeasurementView(APIView):
    serializer_class = ArtifactMeasurementSerializer

    def get(request, *args, **kwargs):
        token_sinch = kwargs['token_sinch']

        print(token_sinch)

        try:
            artifact_measurement = ArtifactMeasurement.objects.get(
                token__exact=token_sinch)
        except ArtifactMeasurement.DoesNotExist:
            artifact_measurement = None

        if artifact_measurement is None:
            response_msg = {
                'details': "El token: " + token_sinch + " ,no existe!",
                "status": status.HTTP_404_NOT_FOUND}
            return Response(response_msg)

        else:
            measurement = {"token": artifact_measurement.token,
                           "weight": artifact_measurement.weight,
                           "body_temperature": artifact_measurement.body_temperature,
                           "blood_pressure": artifact_measurement.blood_pressure,
                           "picture_url": artifact_measurement.picture_url
                           }
            print(measurement)
            return Response(measurement)


# dev
class ArtifactMeasurementTool(APIView):
    serializer_class = ArtifactMeasurementSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data
        print(vd)
        print(vd.get("token"))
        print(vd.get("weight"))
        print(vd.get("body_temperature"))
        print(vd.get("blood_pressure"))
        weight = vd.get("weight")
        body_temperature = vd.get("body_temperature")
        blood_pressure = vd.get("blood_pressure")

        try:
            artifact_measurement = ArtifactMeasurement.objects.get(
                token__exact=vd.get("token"))
        except ArtifactMeasurement.DoesNotExist:
            artifact_measurement = None

        if artifact_measurement is None:
            for key in vd:
                if key == 'weight':
                    artifact = ArtifactMeasurement(token=vd.get("token"),
                                                   weight=vd.get("weight"))
                    artifact.save()
                    response_msg = {'details': "El token: " + vd.get(
                        "token") + " y el peso de: " + vd.get("weight") + "",
                                    "status": status.HTTP_200_OK}
                    return Response(response_msg)

                elif key == 'body_temperature':
                    artifact = ArtifactMeasurement(token=vd.get("token"),
                                                   body_temperature=vd.get(
                                                       "body_temperature"))
                    artifact.save()
                    response_msg = {'details': "El token: " + vd.get(
                        "token") + " y el peso de: " + vd.get(
                        "body_temperature") + "",
                                    "status": status.HTTP_200_OK}
                    return Response(response_msg)

                elif key == 'blood_pressure':
                    artifact = ArtifactMeasurement(token=vd.get("token"),
                                                   blood_pressure=vd.get(
                                                       "blood_pressure"))
                    artifact.save()
                    response_msg = {'details': "El token: " + vd.get(
                        "token") + " y el peso de: " + vd.get(
                        "body_temperature") + "",
                                    "status": status.HTTP_200_OK}
                    return Response(response_msg)

        else:
            for key in vd:
                if key == 'weight':
                    artifact_measurement.weight = vd.get("weight")
                    artifact_measurement.save()
                    response_msg = {
                        'details': "El peso de " + weight + " fue ingresado",
                        "status": status.HTTP_200_OK}
                    return Response(response_msg)

                elif key == 'body_temperature':
                    artifact_measurement.body_temperature = vd.get(
                        "body_temperature")
                    artifact_measurement.save()
                    response_msg = {'details': "El peso de " + vd.get(
                        "body_temperature") + " fue ingresado",
                                    "status": status.HTTP_200_OK}
                    return Response(response_msg)

                elif key == 'blood_pressure':
                    artifact_measurement.blood_pressure = vd.get(
                        "blood_pressure")
                    artifact_measurement.save()
                    response_msg = {'details': "El peso de " + vd.get(
                        "blood_pressure") + " fue ingresado",
                                    "status": status.HTTP_200_OK}
                    return Response(response_msg)

            return Response("this measure can not be finalize")


# check
class MeasurementWeight(APIView):
    serializer_class = ArtifactMeasurementSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data
        print(vd)
        print(vd.get("token"))
        print(vd.get("weight"))

        try:
            artifact_measurement = ArtifactMeasurement.objects.get(
                token__exact=vd.get("token"))
        except ArtifactMeasurement.DoesNotExist:
            artifact_measurement = None

        if artifact_measurement is None:
            artifact = ArtifactMeasurement(token=vd.get("token"),
                                           weight=vd.get("weight"))
            artifact.save()
            response_msg = {'details': "El token: " + vd.get(
                "token") + " y el peso de: " + vd.get("weight") + "",
                            "status": status.HTTP_200_OK}
            return Response(response_msg)

        else:
            artifact_measurement.weight = vd.get("weight")
            artifact_measurement.save()
            response_msg = {
                'details': "El peso de " + vd.get("weight") + " fue ingresado",
                "status": status.HTTP_200_OK}
            return Response(response_msg)


class MeasurementBodyTemperature(APIView):
    serializer_class = ArtifactMeasurementSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data
        print(vd)
        print(vd.get("token"))
        print(vd.get("body_temperature"))

        try:
            artifact_measurement = ArtifactMeasurement.objects.get(
                token__exact=vd.get("token"))
        except ArtifactMeasurement.DoesNotExist:
            artifact_measurement = None

        if artifact_measurement is None:
            artifact = ArtifactMeasurement(token=vd.get("token"),
                                           body_temperature=vd.get(
                                               "body_temperature"))
            artifact.save()
            response_msg = {'details': "El token: " + vd.get(
                "token") + " y la temperatura de: " + vd.get(
                "body_temperature") + "",
                            "status": status.HTTP_200_OK}
            return Response(response_msg)

        else:
            artifact_measurement.body_temperature = vd.get("body_temperature")
            artifact_measurement.save()
            response_msg = {'details': "La temperatura  " + vd.get(
                "body_temperature") + " fue ingresado",
                            "status": status.HTTP_200_OK}
            return Response(response_msg)


# check
class BloodPressure(APIView):
    serializer_class = ArtifactMeasurementSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data
        print(vd)
        print(vd.get("token"))
        print(vd.get("blood_pressure"))

        try:
            artifact_measurement = ArtifactMeasurement.objects.get(
                token__exact=vd.get("token"))
        except ArtifactMeasurement.DoesNotExist:
            artifact_measurement = None

        if artifact_measurement is None:
            artifact = ArtifactMeasurement(token=vd.get("token"),
                                           blood_pressure=vd.get(
                                               "blood_pressure"))
            artifact.save()
            response_msg = {'details': "El token: " + vd.get(
                "token") + " y la temperatura de: " + vd.get(
                "blood_pressure") + "",
                            "status": status.HTTP_200_OK}
            return Response(response_msg)

        else:
            artifact_measurement.blood_pressure = vd.get("blood_pressure")
            artifact_measurement.save()
            response_msg = {'details': "La frecuencia cardiaca  " + vd.get(
                "blood_pressure") + " fue ingresado",
                            "status": status.HTTP_200_OK}
            return Response(response_msg)


# check
class PatientUpdate(APIView):
    """
    Retrieve, update a Patient.
    """

    def get_object(self, pk):
        try:
            return Patient.objects.get(pk=pk)
        except Patient.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        patient = self.get_object(pk)
        serializer = PatientSerializer(patient)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        patient = self.get_object(pk)
        serializer = PatientSerializer(patient, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# check
class CallDoctorView(APIView):
    def get(self, request, *args, **kwargs):
        midoc_user = self.kwargs['midoc_user']
        print(midoc_user)

        try:
            doctor = Doctor.objects.get(midoc_user__exact=midoc_user)
        except Doctor.DoesNotExist:
            doctor = None

        if doctor is None:
            response_msg = {
                'details': "The doctor " + midoc_user + " is not registered ",
                "status": status.HTTP_404_NOT_FOUND}
            return Response(response_msg)

        else:
            dict = {"doctor_name": doctor.doctor_name,
                    "specialty": doctor.emergency_attention.attention_name,
                    "picture_url": doctor.picture_url}

        return Response(dict)


# dev
class CallActivate(APIView):
    # test patch, post
    def get(self, request, *args, **kwargs):
        doctor_id = kwargs["doctor_id"]
        activate = kwargs["activate"]
        activate_bool = validate_one_character(activate)

        if activate_bool is True:
            try:
                doctor = Doctor.objects.get(pk=doctor_id)
            except Doctor.DoesNotExist:
                doctor = None

            if doctor is None:
                response_msg = {
                    'details': "Doctor Id: " + doctor_id + " is not register",
                    # "status": status.HTTP_404_NOT_FOUND}
                    "status": activate}
                return Response(response_msg)
            else:
                doctor.call_activate = activate
                doctor.save()
                response_msg = {
                    'medical_history_registerdetails': "The Doctor Status was updated",
                    # "status": status.HTTP_200_OK}
                    "status": activate}
                return Response(response_msg)
        else:
            response_msg = {
                'details': "value too long for type status character or must be '0' or '1'",
                # "status": status.HTTP_200_OK}
                "status": status.HTTP_403_FORBIDDEN}
            return Response(response_msg)

# -----------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------


# Test General
class PaymentAPIView(APIView):
    def get(self, request, *args, **kwargs):
        card_data = {'card_number': '4111111111111111',
                     'currency_code': 'PEN',
                     'cvv': '123',
                     'expiration_month': 9,
                     'expiration_year': 2020,
                     'last_name': 'Muro',
                     'email': 'nuevo@meme.com',
                     'first_name': 'Will'}

        """
        Creacion del token, este token tiene que ser mandado desde front o 
        mobile, solo por fines de pruebas lo estoy generando en el backend
        """
        token = culqipy.Token.create(card_data)
        print(token)

        dir_refund = {'address': 'av lima 123', 'address_city': 'lima',
                      'country_code': 'PE', 'email': 'nuevo@meme.com',
                      'first_name': 'Will', 'last_name': 'Muro',
                      'metadata': {'test': 'test'}, 'phone_number': 899898999}
        customer = culqipy.Customer.create(dir_refund)
        print(customer)

        dir_card = {'customer_id': customer["id"], 'token_id': token["id"]}
        card = culqipy.Card.create(dir_card)
        print(card)

        dir_subscription = {"card_id": card["id"], "plan_id": "pln_test_CsNFZIRwlEczFfYa"}
        subsbription=culqipy.Subscription.create(dir_subscription)
        print(subsbription)

        return Response({"status": "created ok"})


# Test Genereal
class MakePaymentAPIViewTest(APIView):
    serializer_class = CardInfoSerializer
    #serializer_class = CustomerPaymentInfoSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data

        # mobile generator
        token = culqipy.Token.create(serializer.data)

        # temp variables
        address = "av lima 199"
        address_city = "Lima"
        country_code = "PE"

        # dir_refund = {"address": vd.get("address"), "address_city": vd.get("address_city"),
        #               "country_code": vd.get("country_code"),'email':vd.get("email") ,
        #               "first_name": vd.get("first_name"), "last_name": vd.get("last_name"),
        #               'metadata': {"test": "test"}, 'phone_number': vd.get("phone_number")}
        dir_refund = {"address": address, "address_city": address_city, "country_code": country_code,
                      'email': vd.get("email"), "first_name": vd.get("first_name"),
                      "last_name": vd.get("last_name"),
                      'metadata': {'test': 'test'}, 'phone_number': 666777888}


        customer = culqipy.Customer.create(dir_refund)

        """
        {
            "param": "email",
            "object": "error",
            "type": "parameter_error",
            "merchant_message": "Un cliente esta registrado actualmente con este email."
        }
        
        """
        print(">> Customer")
        print(customer)

        if customer['object'] == 'error':
            response_msg = {'details': customer['merchant_message'], "status": status.HTTP_400_BAD_REQUEST}
            return Response(response_msg)

        else:
            dir_card = {'customer_id': customer["id"], 'token_id': token["id"]}
            card = culqipy.Card.create(dir_card)
            print(">> Card")
            print(card)
            print(card['customer_id'])

            dir_subscription = {"card_id": card["id"], "plan_id": "pln_test_CsNFZIRwlEczFfYa"}
            subsbription = culqipy.Subscription.create(dir_subscription)
            print("Suscription")
            print(subsbription)

            personal_plan.delay(vd.get("email"))

            response_msg = {'details': "Payment Sucess", "status": status.HTTP_400_BAD_REQUEST}

            return Response(subsbription)



# General
class MakePaymentAPIView(APIView):
    #serializer_class = CardInfoSerializer
    serializer_class = CustomerPaymentInfoSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data

        # mobile generator
        # token = culqipy.Token.create(serializer.data)

        dir_refund = {"address": vd.get("address"), "address_city": vd.get("address_city"),
                      "country_code": vd.get("country_code"),'email':vd.get("email") ,
                      "first_name": vd.get("first_name"), "last_name": vd.get("last_name"),
                      'metadata': {"test": "test"}, 'phone_number': vd.get("phone_number")}

        customer = culqipy.Customer.create(dir_refund)


        print(">> Customer")
        print(customer)

        if customer['object'] == 'error':
            response_msg = {'details': customer['merchant_message'], "status": status.HTTP_400_BAD_REQUEST}
            return Response(response_msg)

        else:
            dir_card = {'customer_id': customer["id"], 'token_id': vd.get("token_id")}
            card = culqipy.Card.create(dir_card)
            print(">> Card")
            print(card)
            print(card['customer_id'])

            dir_subscription = {"card_id": card["id"], "plan_id": "pln_test_CsNFZIRwlEczFfYa"}
            subsbription = culqipy.Subscription.create(dir_subscription)
            print("Suscription")
            print(subsbription)

            plan = Plan.objects.get(plantype=vd.get('plan'))
            if plan:
                plan_amount = plan.amount
                payment = PaymentTransaction(plan=plan.plantype_id, first_name=vd.get("first_name"), last_name=vd.get("last_name"),
                                   email=vd.get("first_name"), amount=plan_amount,phone_number= vd.get("phone_number"),
                                   address_city=vd.get("address_city"), address =vd.get("address"))
                payment.save()

            personal_plan.delay(vd.get("email"), vd.get("first_name"), vd.get("last_name"))


            return Response(subsbription)





# General
class GetCallStates(APIView):
    serializer_class = DoctorSerializer

    def get(self, request, *args, **kwargs):
        doctor_id = self.kwargs['doctor_id']

        try:
            doctor = Doctor.objects.get(pk=doctor_id)
        except Doctor.DoesNotExist:
            doctor = None

        if doctor:
            serializer = self.serializer_class(doctor)
            return Response(serializer.data)

        else:
            response_msg = {'details': 'El doctor que buscas no exite','status': status.HTTP_404_NOT_FOUND}
            return HttpResponse(json.dumps(response_msg, cls=DjangoJSONEncoder),content_type='application/json')


# General
class UpdateDoctorCallStatus(APIView):
    """
    Retrieve, update a Doctor instance.
    """

    def get_object(self, pk):
        try:
            return Doctor.objects.get(pk=pk)
        except Doctor.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        doctor = self.get_object(pk)
        serializer = DoctorSerializer(doctor)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        doctor = self.get_object(pk)
        serializer = DoctorSerializer(doctor, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# General
class DoctorCallQueue(APIView):
    """
    Retrieve, update a Doctor instance.
    """
    def get_object(self, pk):
        try:
            return Doctor.objects.get(pk=pk)
        except Doctor.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        doctor = self.get_object(pk)
        serializer = DoctorSerializer(doctor)
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):
        doctor = self.get_object(pk)
        serializer = DoctorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data
        print(vd)
        print(vd.get("queue_count"))
        doctor.queue_count = doctor.queue_count + int(vd.get("queue_count"))
        while doctor.queue_count >= 0:
            if doctor.queue_count == 0:
                doctor.in_call = True
                doctor.save()

                response_msg = {'details': 'count updated', 'status': status.HTTP_200_OK}
                return HttpResponse(json.dumps(response_msg, cls=DjangoJSONEncoder), content_type='application/json')

            else:
                doctor.in_call = False
                doctor.save()

                d = {"id": doctor.pk, "cmd_peru": doctor.cmd_peru,
                     "degree": doctor.degree, "doctor_name": doctor.doctor_name,
                     "year_of_birth": doctor.year_of_birth,
                     "picture_url": doctor.picture_url,
                     "location_id": doctor.location_id,
                     "email": doctor.email, "midoc_user": doctor.midoc_user,
                     "password": doctor.password,
                     "type_of_specialist": doctor.type_of_specialist,
                     "is_enabled": doctor.is_enabled,
                     "call_activate": doctor.call_activate,
                     "in_call": doctor.in_call,
                     "queue_count": doctor.queue_count}
                return Response(d)

        response_msg = {'details': 'Negative queue is not allowed', 'status': status.HTTP_403_FORBIDDEN}
        return HttpResponse(json.dumps(response_msg, cls=DjangoJSONEncoder), content_type='application/json')



# General
class PatientLogin(APIView):
    serializer_class = PatientSerializer

    def get(self, request, format=None):
        patient = Patient.objects.all()
        serializer = self.serializer_class(patient, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data

        print(vd)
        print(vd.get("email"))
        print(vd.get("password"))
        try:

            if Patient.objects.filter(password__iexact=vd.get("password")).exists() and \
                    Patient.objects.filter(email__iexact=vd.get("email")).exists():
                patient = Patient.objects.get(email=vd.get("email"))

                print(patient)


                #user = {'username': vd.get("midoc_user")}

                #ticket = getAuthTicket(user)

                # location = Location.objects.get(pk=doctor.location_id)
                # location.enterprise.picture_url_enterprise

                p = {"id": patient.pk, "name": patient.name, "year_of_birth":patient.year_of_birth,
                     "email": patient.email, "midoc_user": patient.midoc_user, "password": patient.password,
                     "dni": patient.dni, "picture_url": patient.picture_url, "blood_type": patient.blood_type,
                     "allergic_reaction": patient.allergic_reaction, "token_sinch": patient.token_sinch,
                     "size": patient.size, "contact_phone": patient.contact_phone, "gender": patient.gender,
                     "is_enterprise_enabled":patient.is_enterprise_enabled, "background": patient.background}
                print(p)
                return Response(p)
                # return HttpResponse(json.dumps(d, cls=DjangoJSONEncoder), content_type='application/json')
            else:
                print(">>> no hay!")
                response_msg = {'details': 'El usuario no existe', 'status': status.HTTP_409_CONFLICT}
                print(response_msg)
                return HttpResponse(
                    json.dumps(response_msg, cls=DjangoJSONEncoder), content_type='application/json')

        except Exception as inst:
            print(inst)
            print(">>> exception block")
            response_msg = {'details': 'User exception', 'status': status.HTTP_409_CONFLICT,
                            "exception": inst}
            print(response_msg)
            return HttpResponse(json.dumps(response_msg, cls=DjangoJSONEncoder), content_type='application/json')


# General
class PatientRegisterView(APIView):
    serializer_class = PatientSerializer

    def get(self, format=None):
        serializer = self.serializer_class(Patient.objects.all(), many=True)
        return Response(serializer.data)

    #@transaction.atomic()
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data

        try:
            if not Patient.objects.filter(email__iexact=vd.get("email")).exists():
                print("object to save: {}".format(vd))
                # save and get the recent id
                patient = serializer.save()
                print(patient.email)
                # patient.pk get the recent id

                welcome.delay(patient.email, patient.name)

                p = {"id": patient.pk, "name": patient.name, "year_of_birth": patient.year_of_birth,
                     "email": patient.email, "midoc_user": patient.midoc_user, "password": patient.password,
                     "dni": patient.dni, "picture_url": patient.picture_url, "blood_type": patient.blood_type,
                     "allergic_reaction": patient.allergic_reaction, "token_sinch": patient.token_sinch,
                     "size": patient.size, "contact_phone": patient.contact_phone, "gender": patient.gender,
                     "is_enterprise_enabled": patient.is_enterprise_enabled, "background": patient.background}
                print(p)
                # return HttpResponse(json.dumps(p, cls=DjangoJSONEncoder), content_type='application/json')
                return Response(p)

            else:
                print(">>> Usuario ya se encuentra registrado")
                response_msg = {'details': 'Este Usuario ya esta registrado', 'status': status.HTTP_409_CONFLICT}
                return HttpResponse(json.dumps(response_msg, cls=DjangoJSONEncoder), content_type='application/json')

        except Exception as inst:
            print(">>> create failure")
            print(inst)
            response_msg = [{'create': 'failure'}]
            return HttpResponse(json.dumps(response_msg, cls=DjangoJSONEncoder), content_type='application/json')


# General
class RecoveryEmailView(APIView):
    serializer_class = RecoveryEmailSerializer


    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data
        print(vd)
        print(vd.get("patient"))

        try:
            rm = RecoveryEmail(patient=vd.get("patient"), code=code_generator())
            rm.save()

            recovery.delay(rm.patient.email, rm.code)

            response_msg = {'details': 'El codigo de verificacion fue creado con exito', 'status': status.HTTP_200_OK}
            return HttpResponse(json.dumps(response_msg, cls=DjangoJSONEncoder), content_type='application/json')


        except Exception as inst:
            response_msg = [{'create': 'failure'}]
            return HttpResponse(json.dumps(response_msg, cls=DjangoJSONEncoder), content_type='application/json')

# General
# sent the code and the patient id
class ResponseEmailCode(APIView):
    serializer_class = RecoveryEmailSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data
        print(vd)
        print(vd.get("code"))
        print(vd.get("patient"))

        try:
            re = RecoveryEmail.objects.get(code=vd.get("code"))
            if re and re.is_used == False and re.patient.pk == int(vd.get("patient")):
                re.is_used = True
                re.save()
                response_msg = {'details': 'El codigo de verificacion fue usado con éxito','status': status.HTTP_200_OK}
                return HttpResponse(json.dumps(response_msg, cls=DjangoJSONEncoder), content_type='application/json')
            else:
                response_msg = {'details': 'Este codigo es inválido', 'status': status.HTTP_403_FORBIDDEN}
                return HttpResponse(json.dumps(response_msg, cls=DjangoJSONEncoder), content_type='application/json')

        except Exception as inst:
            response_msg = [{'create': 'verification failure'}]
            return HttpResponse(json.dumps(response_msg, cls=DjangoJSONEncoder), content_type='application/json')

class UpdateEmailPassword(APIView):

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data
        print(vd)
        print(vd.get("password"))
        print(vd.get("patient_id"))
        try:
            patient = Patient.objects.get(pk=vd.get("patient_id"))
            if patient:
                patient.password = vd.get("password")
                patient.save()
                response_msg = {'details': 'El Password se actualizo con exito','status': status.HTTP_200_OK}
                return HttpResponse(json.dumps(response_msg, cls=DjangoJSONEncoder), content_type='application/json')

            else:
                response_msg = {'details': 'Este paciente no existe', 'status': status.HTTP_404_NOT_FOUND}
                return HttpResponse(json.dumps(response_msg, cls=DjangoJSONEncoder), content_type='application/json')



        except Exception as inst:
            response_msg = [{'create': 'verification failure'}]
            return HttpResponse(json.dumps(response_msg, cls=DjangoJSONEncoder), content_type='application/json')







