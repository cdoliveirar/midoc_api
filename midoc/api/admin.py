from django.contrib import admin

# Register your models here.
from django.contrib import admin

# Register your models here.

from .models import Voucher, VoucherType


admin.site.register(Voucher)
admin.site.register(VoucherType)

