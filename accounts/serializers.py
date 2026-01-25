# accounts/serializers.py
from rest_framework import serializers
from .models import User, CommitteeReport

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # These are the fields the API will share
        fields = ['id', 'username', 'membership_tier', 'is_verified', 'phone_number']

class CommitteeReportSerializer(serializers.ModelSerializer):
    # This pulls the committee name instead of just the ID number
    committee_name = serializers.CharField(source='committee.name', read_only=True)
    
    class Meta:
        model = CommitteeReport
        fields = ['id', 'committee_name', 'title', 'file', 'uploaded_at']