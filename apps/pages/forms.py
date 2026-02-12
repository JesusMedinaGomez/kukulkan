from django import forms
from .models import MensajeContacto

class ContactoForm(forms.ModelForm):
    class Meta:
        model = MensajeContacto
        fields = ['nombre', 'email', 'asunto', 'asunto_personalizado', 'mensaje']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-xl focus:ring-2 focus:ring-gold focus:border-transparent transition-all duration-200',
                'placeholder': 'Ej. Juan Pérez'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-xl focus:ring-2 focus:ring-gold focus:border-transparent transition-all duration-200',
                'placeholder': 'hermano@ejemplo.com'
            }),
            'asunto': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-xl focus:ring-2 focus:ring-gold focus:border-transparent transition-all duration-200'
            }),
            'asunto_personalizado': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-xl focus:ring-2 focus:ring-gold focus:border-transparent transition-all duration-200',
                'placeholder': 'Especifica tu asunto'
            }),
            'mensaje': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-xl focus:ring-2 focus:ring-gold focus:border-transparent transition-all duration-200 resize-none',
                'placeholder': 'Escribe tu mensaje con respeto y fraternidad...',
                'rows': 5
            }),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        asunto = cleaned_data.get('asunto')
        asunto_personalizado = cleaned_data.get('asunto_personalizado')
        
        if asunto == 'otro' and not asunto_personalizado:
            self.add_error('asunto_personalizado', 'Especifica el asunto de tu mensaje')
        
        return cleaned_data