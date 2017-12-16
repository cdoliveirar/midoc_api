from django.db import models
from django.utils import timezone


class Doctor(models.Model):
    emergency_attention = models.ForeignKey('EmergencyAttention', models.DO_NOTHING, blank=True, null=True)
    location_id = models.IntegerField(unique=True, blank=True, null=True)
    cmd_peru = models.CharField(max_length=20, blank=True, null=True)
    degree = models.CharField(max_length=100, blank=True, null=True)
    doctor_name = models.CharField(max_length=100, blank=True, null=True)
    year_of_birth = models.DateField(blank=True, null=True)
    picture_url = models.TextField(blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    midoc_user = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=100, blank=True, null=True)
    type_of_specialist = models.CharField(max_length=100, blank=True, null=True)
    call_activate = models.CharField(max_length=1, blank=True, null=True)
    is_enabled = models.NullBooleanField()
    in_call = models.NullBooleanField()
    queue_count = models.IntegerField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.TextField(blank=True, null=True)
    last_modified_date = models.DateTimeField(auto_now=True)
    last_modified_by = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{0} - {1}".format(self.doctor_name, self.type_of_specialist)

    class Meta:
        managed = False
        db_table = 'doctor'


class EmergencyAttention(models.Model):
    attention_type_id = models.CharField(max_length=80, blank=True, null=True)
    attention_name = models.CharField(max_length=80, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    picture_url = models.TextField(blank=True, null=True)
    is_enabled = models.NullBooleanField()
    is_emergency = models.NullBooleanField()
    created_date = models.DateTimeField(blank=True, null=True)
    created_by = models.TextField(blank=True, null=True)
    last_modified_date = models.DateTimeField(blank=True, null=True)
    last_modified_by = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'emergency_attention'


class Enterprise(models.Model):
    parent = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)
    license = models.ForeignKey('License', models.DO_NOTHING, blank=True, null=True)
    enterprise_level = models.IntegerField(blank=True, null=True)
    picture_url_enterprise = models.TextField(blank=True, null=True)
    ruc = models.CharField(max_length=11, blank=True, null=True)
    business_name = models.CharField(max_length=255, blank=True, null=True)
    web_page = models.CharField(max_length=100, blank=True, null=True)
    trade_name = models.CharField(max_length=100, blank=True, null=True)
    comercial_activity = models.CharField(max_length=50, blank=True, null=True)
    postal_address = models.CharField(max_length=255, blank=True, null=True)
    contact_name = models.CharField(max_length=255, blank=True, null=True)
    contact_phone = models.CharField(max_length=30, blank=True, null=True)
    midoc_user = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=100, blank=True, null=True)
    created_date = models.DateTimeField(blank=True, null=True)
    created_by = models.TextField(blank=True, null=True)
    last_modified_date = models.DateTimeField(blank=True, null=True)
    last_modified_by = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{0} - {1}".format(self.business_name, self.comercial_activity)

    class Meta:
        managed = False
        db_table = 'enterprise'


class License(models.Model):
    code = models.IntegerField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    final_date = models.DateField(blank=True, null=True)
    access_number = models.IntegerField(blank=True, null=True)
    created_date = models.DateTimeField(blank=True, null=True)
    created_by = models.TextField(blank=True, null=True)
    last_modified_date = models.DateTimeField(blank=True, null=True)
    last_modified_by = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{0} - {1}".format(self.code, self.access_number)

    class Meta:
        managed = False
        db_table = 'license'


class Location(models.Model):
    enterprise = models.ForeignKey(Enterprise, models.DO_NOTHING, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    picture_url = models.TextField(blank=True, null=True)
    is_enabled = models.NullBooleanField()
    postal_address = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(blank=True, null=True)
    created_by = models.TextField(blank=True, null=True)
    last_modified_date = models.DateTimeField(blank=True, null=True)
    last_modified_by = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'location'


# check
class LocationEmergencyAttention(models.Model):
    # location = models.ForeignKey(Location, models.DO_NOTHING, primary_key=True)
    # emergency_attention = models.ForeignKey(EmergencyAttention, models.DO_NOTHING)
    location = models.ForeignKey(Location)
    emergency_attention = models.ForeignKey(EmergencyAttention)
    created_date = models.DateTimeField(blank=True, null=True)
    created_by = models.TextField(blank=True, null=True)
    last_modified_date = models.DateTimeField(blank=True, null=True)
    last_modified_by = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'location_emergency_attention'
        unique_together = (('location', 'emergency_attention'),)


#check
class MedicalHistory(models.Model):
    patient = models.ForeignKey('Patient', models.DO_NOTHING, related_name="patients_medical_histories" )
    doctor = models.ForeignKey(Doctor, models.DO_NOTHING, related_name="doctors")
    emergencista = models.ForeignKey(Doctor, models.DO_NOTHING, related_name='emergencistas')
    location_id = models.IntegerField(unique=True, blank=True, null=True)
    medical_history_text = models.TextField(blank=True, null=True)
    symptom = models.TextField(blank=True, null=True)
    doctor_comment = models.TextField(blank=True, null=True)
    diagnostic = models.TextField(blank=True, null=True)
    weight = models.CharField(max_length=10, blank=True, null=True)
    body_temperature = models.CharField(max_length=10, blank=True, null=True)
    blood_pressure = models.CharField(max_length=10, blank=True, null=True)
    heart_rate = models.CharField(max_length=10, blank=True, null=True)
    next_medical_date = models.DateTimeField(blank=True, null=True, default=timezone.now)
    #created_date = models.DateTimeField(blank=True, null=True, default=timezone.now)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.TextField(blank=True, null=True)
    last_modified_date = models.DateTimeField(auto_now=True)
    last_modified_by = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{0} - {1} - {2}".format(self.created_date, self.diagnostic, self.doctor)

    #def save(self, *args, **kwargs):
    #    super(MedicalHistory, self).save(*args, **kwargs)

    class Meta:
        managed = False
        db_table = 'medical_history'


class MedicalHistoryMedia(models.Model):
    medical_history = models.ForeignKey(MedicalHistory, models.DO_NOTHING, blank=True, null=True)
    picture_url = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(blank=True, null=True)
    created_by = models.TextField(blank=True, null=True)
    last_modified_date = models.DateTimeField(blank=True, null=True)
    last_modified_by = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'medical_history_media'


class Patient(models.Model):
    location = models.ForeignKey(Location, models.DO_NOTHING, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    year_of_birth = models.DateField(blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    midoc_user = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=100, blank=True, null=True)
    dni = models.CharField(max_length=20, blank=True, null=True)
    picture_url = models.TextField(blank=True, null=True)
    blood_type = models.TextField(blank=True, null=True)
    allergic_reaction = models.TextField(blank=True, null=True)
    token_sinch = models.CharField(max_length=100, blank=True, null=True)
    size = models.CharField(max_length=100, blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=1, blank=True, null=True)
    is_enterprise_enabled = models.NullBooleanField()
    background = models.TextField(blank=True, null=True)
    count_calling = models.IntegerField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.TextField(blank=True, null=True)
    last_modified_date = models.DateTimeField(auto_now=True)
    last_modified_by = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{0} - {1}".format(self.name, self.blood_type, self.allergic_reaction)

    class Meta:
        managed = False
        db_table = 'patient'


class Appointment(models.Model):
    patient = models.ForeignKey('Patient', models.DO_NOTHING, blank=True, null=True)
    doctor = models.ForeignKey('Doctor', models.DO_NOTHING, blank=True, null=True)
    appointment_time = models.DateTimeField(blank=True, null=True)
    appointment_status = models.CharField(max_length=20, blank=True, null=True)
    created_date = models.DateTimeField(blank=True, null=True)
    created_by = models.TextField(blank=True, null=True)
    last_modified_date = models.DateTimeField(blank=True, null=True)
    last_modified_by = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{0} - {1}".format(self.patient.name, self.doctor.doctor_name)

    class Meta:
        managed = False
        db_table = 'appointment'


# without model
#class PatientVerify(object):
#    def __init__(self, dni, enterprise_id, created=None):
#        self.dni = dni
#        self.enterprise_id = enterprise_id



class ArtifactMeasurement(models.Model):
    token = models.TextField(blank=True, null=True)
    weight = models.CharField(max_length=10, blank=True, null=True)
    body_temperature = models.CharField(max_length=10, blank=True, null=True)
    blood_pressure = models.CharField(max_length=10, blank=True, null=True)
    picture_url = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'artifact_measurement'



class Competition(models.Model):
    patient = models.ForeignKey('Patient', models.DO_NOTHING, blank=True, null=True)
    doctor = models.ForeignKey('Doctor', models.DO_NOTHING, blank=True, null=True)
    qualification = models.IntegerField(blank=True, null=True)
    qualification_feedback = models.CharField(max_length=100, blank=True, null=True)
    recommendation = models.IntegerField(blank=True, null=True)
    recommendation_feedback = models.CharField(max_length=100, blank=True, null=True)
    created_date = models.DateTimeField(blank=True, null=True)
    created_by = models.TextField(blank=True, null=True)
    last_modified_date = models.DateTimeField(blank=True, null=True)
    last_modified_by = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'competition'


class Voucher(models.Model):
    voucher_type = models.ForeignKey('VoucherType', models.DO_NOTHING, blank=True, null=True)
    name = models.CharField(max_length=128, blank=True, null=True)
    code = models.CharField(max_length=128, blank=True, null=True)
    usage = models.CharField(max_length=128, blank=True, null=True)
    state = models.CharField(max_length=1, blank=True, null=True)
    device_id = models.TextField(blank=True, null=True)
    start_datetime = models.DateTimeField(blank=True, null=True)
    end_datetime = models.DateTimeField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{0} - {1}".format(self.name, self.code)

    class Meta:
        managed = False
        db_table = 'voucher'


class VoucherEnterprise(models.Model):
    voucher = models.ForeignKey(Voucher, models.DO_NOTHING)
    enterprise = models.ForeignKey(Enterprise, models.DO_NOTHING)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'voucher_enterprise'


class VoucherType(models.Model):
    id = models.CharField(primary_key=True, max_length=80)
    voucher_type = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{0} - {1}".format(self.description, self.id)

    class Meta:
        managed = False
        db_table = 'voucher_type'



class PaymentTransaction(models.Model):
    plan = models.ForeignKey('Plan', models.DO_NOTHING, blank=True, null=True)
    first_name = models.CharField(max_length=128, blank=True, null=True)
    last_name = models.CharField(max_length=128, blank=True, null=True)
    email = models.CharField(max_length=30, blank=True, null=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    address_city = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=250, blank=True, null=True)
    country_code = models.CharField(max_length=20, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'payment_transaction'


class Plan(models.Model):
    amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    plantype = models.ForeignKey('Plantype', models.DO_NOTHING, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'plan'


class Plantype(models.Model):
    id = models.CharField(primary_key=True, max_length=80)
    name = models.CharField(max_length=128, blank=True, null=True)
    description = models.CharField(max_length=128, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'plantype'


class RecoveryEmail(models.Model):
    patient = models.ForeignKey(Patient, models.DO_NOTHING, blank=True, null=True)
    code = models.CharField(max_length=20, blank=True, null=True)
    is_used = models.NullBooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'recovery_email'
