from django import forms
from .models import Ticket, TicketPriority, TicketComment, TicketAttachment, TicketAssignment
from departments.models import Department, TicketCategory
from accounts.models import User, Role

class TicketCreateForm(forms.ModelForm):
    """
    Multi-section form for reporting workplace/plant issues.
    """
    attachment = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'id': 'ticket-file-input',
            'accept': '.jpg,.jpeg,.png,.pdf,.docx,.xlsx'
        }),
        help_text="Supported: JPG, PNG, PDF, DOCX, XLSX (Max 10MB)"
    )

    class Meta:
        model = Ticket
        fields = [
            'title', 'description', 'department', 'category',
            'building', 'floor', 'room_area', 'equipment_number',
            'priority'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Brief summary of the issue (e.g. Paper Machine 2 Drive Trip)',
                'id': 'id_title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Explain what happened, any symptoms, alarms, or error codes observed...',
                'id': 'id_description'
            }),
            'department': forms.Select(attrs={
                'class': 'form-select form-select-lg',
                'id': 'id_department'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_category'
            }),
            'building': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Building / Mill Section (e.g. Paper Mill #2)',
                'id': 'id_building'
            }),
            'floor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Floor / Level (e.g. Ground Floor, Operating Deck)',
                'id': 'id_floor'
            }),
            'room_area': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Room / Bay / Area (e.g. Dry End, MCC Room 4)',
                'id': 'id_room_area'
            }),
            'equipment_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tag / Equipment ID (e.g. PM2-DRV-04, PUMP-101)',
                'id': 'id_equipment_number'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select form-select-lg',
                'id': 'id_priority'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].queryset = Department.objects.filter(is_active=True)
        self.fields['priority'].queryset = TicketPriority.objects.all().order_by('order')

        # Initially empty categories or populated if department selected
        if 'department' in self.data:
            try:
                dept_id = int(self.data.get('department'))
                self.fields['category'].queryset = TicketCategory.objects.filter(department_id=dept_id, is_active=True)
            except (ValueError, TypeError):
                self.fields['category'].queryset = TicketCategory.objects.none()
        elif self.instance.pk and self.instance.department:
            self.fields['category'].queryset = self.instance.department.categories.filter(is_active=True)
        else:
            self.fields['category'].queryset = TicketCategory.objects.none()

    def clean_attachment(self):
        file = self.cleaned_data.get('attachment')
        if file:
            # 10MB limit
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("Attachment exceeds the maximum 10MB file size limit.")
            ext = file.name.split('.')[-1].lower()
            allowed = ['jpg', 'jpeg', 'png', 'pdf', 'docx', 'xlsx']
            if ext not in allowed:
                raise forms.ValidationError(f"File format .{ext} is not supported. Allowed formats: {', '.join(allowed)}")
        return file


class TicketAssignForm(forms.Form):
    """
    Form for HR / Helpdesk to assign a technician and adjust priority.
    """
    technician = forms.ModelChoiceField(
        queryset=User.objects.filter(role=Role.TECHNICIAN, is_active=True),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_technician'}),
        empty_label="-- Select Recommended Technician --"
    )
    priority = forms.ModelChoiceField(
        queryset=TicketPriority.objects.all().order_by('order'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_assign_priority'}),
        help_text="Optionally adjust priority and SLA commitment"
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Add instructions or context for the technician...'
        })
    )


class TicketResolveForm(forms.Form):
    """
    Form for technicians to record resolution details and upload proof.
    """
    resolution_summary = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Detail what actions were taken (e.g. replaced worn bearing, calibrated sensor, reset drive parameters)...',
            'id': 'id_resolution_summary'
        }),
        help_text="Provide a clear description of the work completed."
    )
    proof_image = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.jpg,.jpeg,.png,.pdf'}),
        help_text="Upload photo or document proving resolution (before/after photo, test report)"
    )


class TicketCommentForm(forms.ModelForm):
    """
    Form to add communication messages to a ticket.
    """
    attachment = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control form-control-sm', 'accept': '.jpg,.jpeg,.png,.pdf,.docx,.xlsx'})
    )

    class Meta:
        model = TicketComment
        fields = ['comment', 'is_internal']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Type your message or inquiry regarding this ticket...'
            }),
            'is_internal': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


class TicketReopenForm(forms.Form):
    """
    Form for employees to reopen an un-resolved ticket.
    """
    reopen_reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Explain why the issue is not resolved or if it reoccurred...'
        }),
        help_text="Please describe why resolution could not be confirmed."
    )
