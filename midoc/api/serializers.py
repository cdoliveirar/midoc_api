from rest_framework import serializers
from .models import (Patient,
                     Doctor,
                     Enterprise,
                     MedicalHistory,
                     ArtifactMeasurement,
                     Competition,
                     Voucher,
                     RecoveryEmail,

                     )



class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'


class EnterpriseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enterprise
        fields = '__all__'


class DoctorLocalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ('id', 'doctor_name', 'picture_url')


class MedicalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalHistory
        fields = '__all__'
        #depth = 1


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'


# without model
class PatientVerifySerializer(serializers.Serializer):
    dni = serializers.CharField(max_length=8)
    enterprise_id = serializers.IntegerField()


# artifact
class ArtifactMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtifactMeasurement
        fields = '__all__'



# --
class MedicalHistoryUpdatingSerializer(serializers.ModelSerializer):

    class Meta:
        model = MedicalHistory
        fields = ('medical_history_text', 'symptom', 'doctor_comment', 'diagnostic', 'weight', 'body_temperature',
                  'blood_pressure', 'heart_rate')


class PatientUpdatingSerializer(serializers.ModelSerializer):
    patients_medical_histories = MedicalHistoryUpdatingSerializer(many=True)

    class Meta:
        model = Patient
        fields = ('name', 'email', 'dni', 'blood_type', 'allergic_reaction','size','contact_phone','gender',
                  'patients_medical_histories')

    def create(self, validated_data):
        patients_medical_histories = validated_data.pop('patients_medical_histories')
        patient = Patient.objects.create(**validated_data)
        for medical_history in patients_medical_histories:
            MedicalHistory.objects.create(patient=patient, **medical_history)
        return patient


class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = '__all__'
        #fields = ('id', 'patient', 'doctor', 'qualification', 'qualification_feedback', 'recommendation',
        #              'recommendation_feedback')




# start - create json nested serializer

# class MedicalHistoryUpdatingSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = MedicalHistory
#         fields = ('medical_history_text', 'symptom', 'doctor_comment', 'diagnostic', 'weight', 'body_temperature',
#                   'blood_pressure', 'heart_rate')
#
#
# class PatientUpdatingSerializer(serializers.ModelSerializer):
#     patients_medical_histories = MedicalHistoryUpdatingSerializer(many=True)
#
#     class Meta:
#         model = Patient
#         fields = ('name', 'email', 'dni', 'blood_type', 'allergic_reaction','size','contact_phone','gender',
#                   'patients_medical_histories')
#
#     def create(self, validated_data):
#         patients_medical_histories = validated_data.pop('patients_medical_histories')
#         patient = Patient.objects.create(**validated_data)
#         for medical_history in patients_medical_histories:
#             MedicalHistory.objects.create(patient=patient, **medical_history)
#         return patient

# end - create json nested serializer
#
#
# {
#     "name": "Carlos Oliveira",
#     "email": "cdoliveirar@gmail.com",
#     "dni": "cdoliveirar@gmail.com",
#     "blood_type": "A-",
#     "allergic_reaction": "No Alergias",
#     "size": "1.78",
#     "contact_phone": "931118101",
#     "gender": "M",
#
#     "patients_medical_histories": [{
#         "medical_history_text": "",
#        	"symptom": "fiebre intensa",
#         "doctor_comment": "aplicar medicina",
#         "diagnostic": "recuperacion",
#         "weight": "89",
#         "body_temperature": "37.2",
#         "blood_pressure": "40/100",
#         "heart_rate": "56"
#         }
#     ]
# }
# --

class MedicalHistorySerializer2(serializers.ModelSerializer):
    class Meta:
        model = MedicalHistory
        fields = ('id','doctor_id','medical_history_text','symptom','doctor_comment','diagnostic', 'weight',
                  'body_temperature', 'blood_pressure', 'heart_rate')


class PatientSerializer2(serializers.ModelSerializer):
    patients_medical_histories = MedicalHistorySerializer2(many=True)

    class Meta:
        model = Patient
        fields = ('id', 'name', 'year_of_birth', 'email', 'midoc_user', 'password', 'dni', 'picture_url', 'blood_type',
                  'allergic_reaction', 'token_sinch', 'size', 'contact_phone', 'gender', 'created_date',
                  'patients_medical_histories')

    def create(self, validated_data):
        patients_medical_histories = validated_data.pop('patients_medical_histories')
        patient = Patient.objects.create(**validated_data)
        for medical_history in patients_medical_histories:
            MedicalHistory.objects.create(patient=patient, **medical_history)
        return patient

    def update(self, instance, validated_data):
        # try:
        medical_histories_data = validated_data.pop('patients_medical_histories')
        medical_histories = (instance.patients_medical_histories).all()
        medical_histories = list(medical_histories)
        # validated_data.get()

        instance.name = validated_data.get('name', instance.name)
        instance.year_of_birth = validated_data.get('year_of_birth', instance.year_of_birth)
        instance.email = validated_data.get('email', instance.email)
        instance.midoc_user = validated_data.get('midoc_user', instance.midoc_user)
        instance.password = validated_data.get('password', instance.password)
        instance.dni = validated_data.get('dni', instance.dni)
        instance.picture_url = validated_data.get('picture_url', instance.picture_url)
        instance.blood_type = validated_data.get('blood_type', instance.blood_type)
        instance.allergic_reaction = validated_data.get('allergic_reaction', instance.allergic_reaction)
        instance.token_sinch = validated_data.get('token_sinch', instance.token_sinch)
        instance.size = validated_data.get('size', instance.size)
        instance.contact_phone = validated_data.get('contact_phone', instance.contact_phone)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.background = validated_data.get('background', instance.background)
        instance.created_date = validated_data.get('created_date', instance.created_date)
        instance.save()


        #if medical_histories:
        for medical_history_data in medical_histories_data:
            #mh = medical_histories.pop(0)
            mh_id = medical_history_data.get('id', None)
            if mh_id:
                mh = MedicalHistory.objects.get(id=mh_id, patient=instance)
                mh.doctor_id = medical_history_data.get('doctor_id', mh.doctor_id)
                mh.medical_history_text = medical_history_data.get('medical_history_text', mh.medical_history_text)
                mh.symptom = medical_history_data.get('symptom', mh.symptom)
                mh.doctor_comment = medical_history_data.get('doctor_comment', mh.doctor_comment)
                mh.diagnostic = medical_history_data.get('diagnostic', mh.diagnostic)
                mh.weight = medical_history_data.get('weight', mh.weight)
                mh.body_temperature = medical_history_data.get('body_temperature', mh.body_temperature)
                mh.blood_pressure = medical_history_data.get('blood_pressure', mh.blood_pressure)
                mh.heart_rate = medical_history_data.get('heart_rate', mh.heart_rate)
                mh.save()
            else:
                print("creando nuevo MH")
                MedicalHistory.objects.create(patient=instance, **medical_history_data)
        return instance


class VoucherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voucher
        fields = '__all__'


# Test for frontend and mobile token generator
class CardInfoSerializer(serializers.Serializer):
    card_number = serializers.CharField(max_length=16)
    cvv = serializers.CharField(max_length=3)
    expiration_month = serializers.CharField(max_length=3)
    expiration_year = serializers.CharField(max_length=4)
    email = serializers.CharField(max_length=250)
    currency_code = serializers.CharField(max_length=3)
    last_name = serializers.CharField(max_length=50)
    first_name = serializers.CharField(max_length=50)


# Begin Tx within Culqi
class CustomerPaymentInfoSerializer(serializers.Serializer):
    first_name= serializers.CharField(max_length=100)
    last_name= serializers.CharField(max_length=100)
    email= serializers.CharField(max_length=250)
    address= serializers.CharField(max_length=250)
    address_city= serializers.CharField(max_length=50)
    country_code= serializers.CharField(max_length=4)
    phone_number= serializers.CharField(max_length=20)
    token_id = serializers.CharField(max_length=250)


class RecoveryEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecoveryEmail
        fields = '__all__'