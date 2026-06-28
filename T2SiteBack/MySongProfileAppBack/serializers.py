from rest_framework import serializers
from .models import Song, User, SongList

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'senha']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'firstName', 'lastName', 'gender', 'email']


class SongSerializer(serializers.ModelSerializer):
    """Serializer para criar, editar e listar músicas"""
    
    class Meta:
        model = Song
        fields = ['id', 'name', 'artist', 'gender']

    def validate_name(self, value):
        """Valida o nome da música"""
        if not value or not value.strip():
            raise serializers.ValidationError('O nome da música é obrigatório.')
        if len(value) > 50:
            raise serializers.ValidationError('O nome da música não pode ter mais de 50 caracteres.')
        return value.strip()

    def validate_artist(self, value):
        """Valida o artista"""
        if not value or not value.strip():
            raise serializers.ValidationError('O artista é obrigatório.')
        if len(value) > 30:
            raise serializers.ValidationError('O artista não pode ter mais de 30 caracteres.')
        return value.strip()

    def validate_gender(self, value):
        """Valida o gênero"""
        if not value or not value.strip():
            raise serializers.ValidationError('O gênero é obrigatório.')
        if len(value) > 15:
            raise serializers.ValidationError('O gênero não pode ter mais de 15 caracteres.')
        return value.strip()


class SongListSerializer(serializers.ModelSerializer):
    """Serializer para listar as músicas da playlist"""
    song1 = SongSerializer(read_only=True)
    song2 = SongSerializer(read_only=True)
    song3 = SongSerializer(read_only=True)
    song4 = SongSerializer(read_only=True)
    song5 = SongSerializer(read_only=True)

    class Meta:
        model = SongList
        fields = ['id', 'user', 'song1', 'song2', 'song3', 'song4', 'song5']


class CreateSongListSerializer(serializers.Serializer):
    """Serializer para criar uma lista de 5 músicas"""
    songs = serializers.ListField(
        child=serializers.DictField(),
        min_length=5,
        max_length=5,
    )

    def validate_songs(self, value):
        """Valida a lista de 5 músicas"""
        if len(value) != 5:
            raise serializers.ValidationError('A playlist deve conter exatamente 5 músicas.')
        
        for idx, song_data in enumerate(value, start=1):
            if not isinstance(song_data, dict):
                raise serializers.ValidationError(f'Dados inválidos na música {idx}.')
            
            name = song_data.get('name', '').strip() if isinstance(song_data.get('name'), str) else ''
            artist = song_data.get('artist', '').strip() if isinstance(song_data.get('artist'), str) else ''
            gender = song_data.get('gender', '').strip() if isinstance(song_data.get('gender'), str) else ''
            
            if not name:
                raise serializers.ValidationError(f'O nome da música {idx} é obrigatório.')
            if not artist:
                raise serializers.ValidationError(f'O artista da música {idx} é obrigatório.')
            if not gender:
                raise serializers.ValidationError(f'O gênero da música {idx} é obrigatório.')
            
            if len(name) > 50:
                raise serializers.ValidationError(f'O nome da música {idx} não pode ter mais de 50 caracteres.')
            if len(artist) > 30:
                raise serializers.ValidationError(f'O artista da música {idx} não pode ter mais de 30 caracteres.')
            if len(gender) > 15:
                raise serializers.ValidationError(f'O gênero da música {idx} não pode ter mais de 15 caracteres.')
        
        return value
