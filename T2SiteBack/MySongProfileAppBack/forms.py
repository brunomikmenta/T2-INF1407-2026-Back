from django import forms
from .models import Song, SongList, GENDER_CHOICES


class SongForm(forms.ModelForm):
    """Formulário para criar uma nova música"""
    
    class Meta:
        model = Song
        fields = ['name', 'artist', 'gender']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da música',
                'maxlength': '50',
                'required': True
            }),
            'artist': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Artista',
                'maxlength': '30',
                'required': True
            }),
            'gender': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Gênero (ex: Rock, Pop, Sertanejo)',
                'maxlength': '15',
                'required': True
            }),
        }
        labels = {
            'name': 'Nome da Música',
            'artist': 'Artista',
            'gender': 'Gênero',
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError('O nome da música é obrigatório.')
        if len(name) > 50:
            raise forms.ValidationError('O nome da música não pode ter mais de 50 caracteres.')
        return name

    def clean_artist(self):
        artist = self.cleaned_data.get('artist', '').strip()
        if not artist:
            raise forms.ValidationError('O artista é obrigatório.')
        if len(artist) > 30:
            raise forms.ValidationError('O artista não pode ter mais de 30 caracteres.')
        return artist

    def clean_gender(self):
        gender = self.cleaned_data.get('gender', '').strip()
        if not gender:
            raise forms.ValidationError('O gênero é obrigatório.')
        if len(gender) > 15:
            raise forms.ValidationError('O gênero não pode ter mais de 15 caracteres.')
        return gender


class SongListForm(forms.Form):
    """Formulário para criar uma lista de 5 músicas"""
    
    song1_name = forms.CharField(
        label='Música 1 - Nome',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome da música 1',
            'required': True
        })
    )
    song1_artist = forms.CharField(
        label='Música 1 - Artista',
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Artista da música 1',
            'required': True
        })
    )
    song1_gender = forms.CharField(
        label='Música 1 - Gênero',
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Gênero da música 1',
            'required': True
        })
    )

    song2_name = forms.CharField(
        label='Música 2 - Nome',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome da música 2',
            'required': True
        })
    )
    song2_artist = forms.CharField(
        label='Música 2 - Artista',
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Artista da música 2',
            'required': True
        })
    )
    song2_gender = forms.CharField(
        label='Música 2 - Gênero',
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Gênero da música 2',
            'required': True
        })
    )

    song3_name = forms.CharField(
        label='Música 3 - Nome',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome da música 3',
            'required': True
        })
    )
    song3_artist = forms.CharField(
        label='Música 3 - Artista',
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Artista da música 3',
            'required': True
        })
    )
    song3_gender = forms.CharField(
        label='Música 3 - Gênero',
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Gênero da música 3',
            'required': True
        })
    )

    song4_name = forms.CharField(
        label='Música 4 - Nome',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome da música 4',
            'required': True
        })
    )
    song4_artist = forms.CharField(
        label='Música 4 - Artista',
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Artista da música 4',
            'required': True
        })
    )
    song4_gender = forms.CharField(
        label='Música 4 - Gênero',
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Gênero da música 4',
            'required': True
        })
    )

    song5_name = forms.CharField(
        label='Música 5 - Nome',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome da música 5',
            'required': True
        })
    )
    song5_artist = forms.CharField(
        label='Música 5 - Artista',
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Artista da música 5',
            'required': True
        })
    )
    song5_gender = forms.CharField(
        label='Música 5 - Gênero',
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Gênero da música 5',
            'required': True
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        
        for song_num in range(1, 6):
            name_key = f'song{song_num}_name'
            artist_key = f'song{song_num}_artist'
            gender_key = f'song{song_num}_gender'
            
            name = cleaned_data.get(name_key, '').strip()
            artist = cleaned_data.get(artist_key, '').strip()
            gender = cleaned_data.get(gender_key, '').strip()
            
            if not name or not artist or not gender:
                raise forms.ValidationError(
                    f'Todos os campos da música {song_num} são obrigatórios.'
                )
            
            cleaned_data[name_key] = name
            cleaned_data[artist_key] = artist
            cleaned_data[gender_key] = gender
        
        return cleaned_data


class EditSongForm(forms.Form):
    """Formulário para editar uma música individual"""
    
    name = forms.CharField(
        label='Nome da Música',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome da música',
            'required': True
        })
    )
    artist = forms.CharField(
        label='Artista',
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Artista',
            'required': True
        })
    )
    gender = forms.CharField(
        label='Gênero',
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Gênero (ex: Rock, Pop, Sertanejo)',
            'required': True
        })
    )

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError('O nome da música é obrigatório.')
        if len(name) > 50:
            raise forms.ValidationError('O nome da música não pode ter mais de 50 caracteres.')
        return name

    def clean_artist(self):
        artist = self.cleaned_data.get('artist', '').strip()
        if not artist:
            raise forms.ValidationError('O artista é obrigatório.')
        if len(artist) > 30:
            raise forms.ValidationError('O artista não pode ter mais de 30 caracteres.')
        return artist

    def clean_gender(self):
        gender = self.cleaned_data.get('gender', '').strip()
        if not gender:
            raise forms.ValidationError('O gênero é obrigatório.')
        if len(gender) > 15:
            raise forms.ValidationError('O gênero não pode ter mais de 15 caracteres.')
        return gender
