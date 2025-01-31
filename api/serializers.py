from rest_framework import serializers
from .models import Face, Form, Parent, Child, Staff, Attendance, Pledge, ClearanceCode, Notification, Transaction

# Serializer for the Face model
class FaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Face
        fields = ['id', 'name', 'embedding']

# Serializer for the Form model
class FormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Form
        fields = ['id', 'name', 'classteachernames', 'classteacherphone', 'classdirections', 'created_at', 'updated_at']

# Serializer for the Parent model
class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parent
        fields = ['id', 'name', 'role', 'phone', 'phone2', 'imgurl', 'residence', 'email']

# Serializer for the Child model
class ChildSerializer(serializers.ModelSerializer):
    parent = ParentSerializer()
    form = FormSerializer()

    class Meta:
        model = Child
        fields = ['id', 'name', 'phone', 'parent', 'fees', 'paycode', 'classname', 'created_at', 'form', 'paid', 'expected_fees']

# Serializer for the Staff model
class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ['id', 'name', 'phone', 'imgurl']

# Serializer for the Attendance model
class AttendanceSerializer(serializers.ModelSerializer):
    parent = ParentSerializer()

    class Meta:
        model = Attendance
        fields = ['id', 'date', 'parent', 'checkintype', 'studentcontact', 'reason', 'present', 'time_in', 'time_out', 'created_at', 'updated_at']

# Serializer for the Pledge model
class PledgeSerializer(serializers.ModelSerializer):
    parent = ParentSerializer()

    class Meta:
        model = Pledge
        fields = ['id', 'parent', 'amount', 'created_at', 'updated_at', 'is_paid', 'paid_at', 'expires_at', 'days']

# Serializer for the ClearanceCode model
class ClearanceCodeSerializer(serializers.ModelSerializer):
    parent = ParentSerializer()

    class Meta:
        model = ClearanceCode
        fields = ['id', 'code', 'visitor', 'reason', 'contact', 'visitor_contact', 'relationship', 'parent', 'created_at', 'updated_at', 'expires_at', 'is_used', 'is_active']

# Serializer for the Notification model
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'creator', 'is_read', 'created_at', 'updated_at']

# Serializer for the Transaction model
class TransactionSerializer(serializers.ModelSerializer):
    parent = ParentSerializer()

    class Meta:
        model = Transaction
        fields = ['id', 'parent', 'amount', 'paycode', 'student_name', 'parent_name', 'parent_phone', 'transaction_reference', 'mno_transaction_reference_id', 'issued_receipt_number', 'created_at', 'updated_at', 'is_paid', 'paid_at', 'expires_at', 'days']
