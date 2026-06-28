from MySongProfileAppBack.serializers import CreateSongListSerializer, ProfileSerializer, SongSerializer, UserSerializer
from rest_framework.views import APIView
from MySongProfileAppBack.models import Song, SongList, User
from rest_framework.response import Response
from django.shortcuts import render, redirect
from rest_framework import status
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import AccessToken
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.db.models import Q
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiExample
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import OpenApiTypes
from drf_spectacular.utils import inline_serializer
from rest_framework import serializers

# Create your views here.

authorization_header_parameter = OpenApiParameter(
    name='Authorization',
    type=OpenApiTypes.STR,
    location=OpenApiParameter.HEADER,
    required=True,
    description='Token JWT no formato: Bearer <token>.',
)

song_list_item_schema = inline_serializer(
    name='SongListItemSchema',
    fields={
        'id': serializers.IntegerField(),
        'name': serializers.CharField(),
        'artist': serializers.CharField(),
        'gender': serializers.CharField(),
        'slot': serializers.IntegerField(min_value=1, max_value=5),
    },
)

detail_response_schema = inline_serializer(
    name='DetailResponseSchema',
    fields={
        'detail': serializers.CharField(),
    },
)

song_list_response_schema = inline_serializer(
    name='SongListResponseSchema',
    fields={
        'songs': song_list_item_schema.__class__(many=True),
        'count': serializers.IntegerField(),
        'missing': serializers.IntegerField(),
        'is_complete': serializers.BooleanField(),
    },
)

song_list_create_response_schema = inline_serializer(
    name='SongListCreateResponseSchema',
    fields={
        'detail': serializers.CharField(),
        'songs': song_list_item_schema.__class__(many=True),
        'count': serializers.IntegerField(),
        'missing': serializers.IntegerField(),
        'is_complete': serializers.BooleanField(),
    },
)

song_detail_update_response_schema = inline_serializer(
    name='SongDetailUpdateResponseSchema',
    fields={
        'detail': serializers.CharField(),
        'song': song_list_item_schema,
    },
)

song_detail_delete_response_schema = inline_serializer(
    name='SongDetailDeleteResponseSchema',
    fields={
        'detail': serializers.CharField(),
        'count': serializers.IntegerField(),
        'missing': serializers.IntegerField(),
        'is_complete': serializers.BooleanField(),
    },
)



def get_user_from_token(request):
    print("GET USER FROM TOKEN CALLED")

    auth_header = request.headers.get("Authorization")

    print("AUTH HEADER:", auth_header)

    if not auth_header:
        return None

    try:
        token = auth_header.replace("Bearer ", "")

        access = AccessToken(token)

        print("PAYLOAD:", access.payload)

        user_id = access.get("user_id")

        print("USER ID:", user_id)

        if user_id is None:
            return None

        
        print("TRYING TO FIND USER:", user_id)

        user = User.objects.get(id=int(user_id))

        print("FOUND USER:", user.username)

        return user

    
    except Exception as e:
        print("TOKEN ERROR TYPE:", type(e))
        print("TOKEN ERROR:", repr(e))
        return None



class CadastrarUsuarioView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):

        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():

            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginUsuarioView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')

        if not username or not password:
            return Response({'detail': 'Username e password são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username, senha=password)
            
            print(
                "LOGIN USER:",
                user.id,
                user.username
            )

        except User.DoesNotExist:
            return Response({'detail': 'Usuário ou senha inválidos.'}, status=status.HTTP_401_UNAUTHORIZED)

        
        access = AccessToken()

        access.set_exp()

        access["user_id"] = str(user.id)
        access["username"] = user.username

        return Response(
            {
                "success": True,
                "username": user.username,
                "access": str(access),
            },
            status=status.HTTP_200_OK

)



class LogoutUsuarioView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    
    def post(self, request):
        return Response(
            {'success': True},
            status=status.HTTP_200_OK
        )



class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        email = request.data.get('email', '').strip()

        if not email:
            return Response({'detail': 'E-mail e obrigatorio.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({'detail': 'E-mail nao encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        signer = TimestampSigner(salt='password-reset')
        reset_code = signer.sign(str(user.id))

        return Response(
            {
                'detail': 'Codigo de redefinicao gerado com sucesso.',
                'reset_code': reset_code,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request):
        code = request.data.get('code', '').strip()
        new_password = request.data.get('new_password', '')

        if not code or not new_password:
            return Response(
                {'detail': 'Codigo e nova senha sao obrigatorios.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        signer = TimestampSigner(salt='password-reset')
        try:
            user_id = signer.unsign(code, max_age=1800)
            user = User.objects.get(id=int(user_id))
        except SignatureExpired:
            return Response({'detail': 'Codigo expirado.'}, status=status.HTTP_400_BAD_REQUEST)
        except (BadSignature, ValueError, User.DoesNotExist):
            return Response({'detail': 'Codigo invalido.'}, status=status.HTTP_400_BAD_REQUEST)

        user.senha = new_password
        user.save(update_fields=['senha'])

        return Response({'detail': 'Senha alterada com sucesso.'}, status=status.HTTP_200_OK)


class ProfileView(APIView):
    print("PROFILE VIEW REACHED")
    permission_classes = [AllowAny]

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    @extend_schema(
        summary='Buscar perfil do usuario autenticado',
        description='Retorna os dados do perfil do usuario autenticado a partir do token JWT enviado manualmente no cabecalho Authorization.',
        tags=['Perfil'],
        parameters=[authorization_header_parameter],
        responses={
            200: ProfileSerializer,
            401: detail_response_schema,
        },
    )
    def get(self, request):
       
        user = get_user_from_token(request)

        if not user:

            return Response({'detail': 'Usuario nao autenticado.'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = ProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary='Atualizar perfil do usuario autenticado',
        description='Atualiza parcialmente os dados do perfil do usuario autenticado.',
        tags=['Perfil'],
        parameters=[authorization_header_parameter],
        request=ProfileSerializer,
        responses={
            200: ProfileSerializer,
            400: OpenApiTypes.OBJECT,
            401: detail_response_schema,
        },
        examples=[
            OpenApiExample(
                'Atualizacao de perfil',
                value={
                    'firstName': 'Bruno',
                    'lastName': 'Silva',
                    'gender': 'M',
                    'email': 'bruno@example.com',
                },
                request_only=True,
            ),
        ],
    )
    def put(self, request):
        user = get_user_from_token(request)

        if not user:
            return Response({'detail': 'Usuario nao autenticado.'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = ProfileSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SongListView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def serialize_songlist(self, songlist):
        songs = []

        if not songlist:
            return songs

        for slot in range(1, 6):
            song = getattr(songlist, f'song{slot}')

            if song:
                serialized = SongSerializer(song).data
                serialized['slot'] = slot
                songs.append(serialized)

        return songs

    @extend_schema(
        summary='Listar playlist do usuario autenticado',
        description='Retorna as musicas ja salvas na playlist do usuario e o estado de completude da lista.',
        tags=['SongList'],
        parameters=[authorization_header_parameter],
        responses={
            200: song_list_response_schema,
            401: detail_response_schema,
        },
    )
    def get(self, request):
        user = get_user_from_token(request)

        if not user:
            return Response({'detail': 'Usuario nao autenticado.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            songlist = user.songlist
        except SongList.DoesNotExist:
            songlist = None

        songs = self.serialize_songlist(songlist)
        song_count = len(songs)

        return Response(
            {
                'songs': songs,
                'count': song_count,
                'missing': max(0, 5 - song_count),
                'is_complete': song_count == 5,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary='Salvar playlist com 5 musicas',
        description='Cria ou sobrescreve a playlist do usuario autenticado com exatamente 5 musicas.',
        tags=['SongList'],
        parameters=[authorization_header_parameter],
        request=CreateSongListSerializer,
        responses={
            201: song_list_create_response_schema,
            400: detail_response_schema,
            401: detail_response_schema,
        },
        examples=[
            OpenApiExample(
                'Playlist completa',
                value={
                    'songs': [
                        {'name': 'Numb', 'artist': 'Linkin Park', 'gender': 'Rock'},
                        {'name': 'Billie Jean', 'artist': 'Michael Jackson', 'gender': 'Pop'},
                        {'name': 'Halo', 'artist': 'Beyonce', 'gender': 'Pop'},
                        {'name': 'Pais e Filhos', 'artist': 'Legiao Urbana', 'gender': 'Rock'},
                        {'name': 'Alive', 'artist': 'Pearl Jam', 'gender': 'Grunge'},
                    ],
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        user = get_user_from_token(request)

        if not user:
            return Response({'detail': 'Usuario nao autenticado.'}, status=status.HTTP_401_UNAUTHORIZED)

        songs_data = request.data.get('songs')

        if not isinstance(songs_data, list) or len(songs_data) != 5:
            return Response(
                {'detail': 'A playlist deve conter exatamente 5 musicas.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        validated_songs = []

        for idx, song_data in enumerate(songs_data, start=1):
            if not isinstance(song_data, dict):
                return Response(
                    {'detail': f'Dados invalidos na musica {idx}.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            name = str(song_data.get('name', '')).strip()
            artist = str(song_data.get('artist', '')).strip()
            gender = str(song_data.get('gender', '')).strip()

            if not name or not artist or not gender:
                return Response(
                    {'detail': f'Preencha nome, artista e genero da musica {idx}.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            validated_songs.append({'name': name, 'artist': artist, 'gender': gender})

        songlist, _ = SongList.objects.get_or_create(user=user)

        for slot in range(1, 6):
            setattr(songlist, f'song{slot}', None)

        created_songs = []
        for slot, song_data in enumerate(validated_songs, start=1):
            song = Song.objects.create(
                name=song_data['name'],
                artist=song_data['artist'],
                gender=song_data['gender'],
            )
            setattr(songlist, f'song{slot}', song)
            created_songs.append(song)

        songlist.save()

        songs = []
        for slot, song in enumerate(created_songs, start=1):
            serialized = SongSerializer(song).data
            serialized['slot'] = slot
            songs.append(serialized)

        return Response(
            {
                'detail': 'Playlist salva com sucesso.',
                'songs': songs,
                'count': 5,
                'missing': 0,
                'is_complete': True,
            },
            status=status.HTTP_201_CREATED,
        )


class SongListSongDetailView(APIView):
    print("SONGLIST VIEW REACHED")
    permission_classes = [AllowAny]

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


    def get_song_and_slot(self, user, song_id):
        try:
            songlist = user.songlist
        except SongList.DoesNotExist:
            return None, None, None

        for slot in range(1, 6):
            song = getattr(songlist, f'song{slot}')
            if song and song.id == song_id:
                return songlist, song, slot

        return songlist, None, None

    @extend_schema(
        summary='Atualizar musica da playlist',
        description='Atualiza uma musica especifica da playlist do usuario autenticado usando o id da musica.',
        tags=['SongList'],
        parameters=[
            authorization_header_parameter,
            OpenApiParameter(
                name='song_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Identificador da musica dentro da playlist do usuario.',
            ),
        ],
        request=SongSerializer,
        responses={
            200: song_detail_update_response_schema,
            400: detail_response_schema,
            401: detail_response_schema,
            404: detail_response_schema,
        },
        examples=[
            OpenApiExample(
                'Atualizacao de musica',
                value={
                    'name': 'In the End',
                    'artist': 'Linkin Park',
                    'gender': 'Rock',
                },
                request_only=True,
            ),
        ],
    )
    def put(self, request, song_id):
        user = get_user_from_token(request)

        if not user:
            return Response({'detail': 'Usuario nao autenticado.'}, status=status.HTTP_401_UNAUTHORIZED)

        songlist, song, slot = self.get_song_and_slot(user, song_id)

        if not songlist:
            return Response({'detail': 'Playlist nao encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        if not song:
            return Response({'detail': 'Musica nao encontrada na sua playlist.'}, status=status.HTTP_404_NOT_FOUND)

        updated_name = str(request.data.get('name', song.name)).strip()
        updated_artist = str(request.data.get('artist', song.artist)).strip()
        updated_gender = str(request.data.get('gender', song.gender)).strip()

        if not updated_name or not updated_artist or not updated_gender:
            return Response(
                {'detail': 'Nome, artista e genero sao obrigatorios.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        song.name = updated_name
        song.artist = updated_artist
        song.gender = updated_gender
        song.save(update_fields=['name', 'artist', 'gender'])

        serialized = SongSerializer(song).data
        serialized['slot'] = slot

        return Response(
            {
                'detail': 'Musica atualizada com sucesso.',
                'song': serialized,
            },
            status=status.HTTP_200_OK,
        )
    
    @extend_schema(
        summary='Remover musica da playlist',
        description='Remove uma musica especifica da playlist do usuario autenticado e devolve o novo estado da lista.',
        tags=['SongList'],
        parameters=[
            authorization_header_parameter,
            OpenApiParameter(
                name='song_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Identificador da musica dentro da playlist do usuario.',
            ),
        ],
        responses={
            200: song_detail_delete_response_schema,
            401: detail_response_schema,
            404: detail_response_schema,
        },
    )
    def delete(self, request, song_id):
        user = get_user_from_token(request)

        if not user:
            return Response({'detail': 'Usuario nao autenticado.'}, status=status.HTTP_401_UNAUTHORIZED)

        songlist, song, slot = self.get_song_and_slot(user, song_id)

        if not songlist:
            return Response({'detail': 'Playlist nao encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        if not song:
            return Response({'detail': 'Musica nao encontrada na sua playlist.'}, status=status.HTTP_404_NOT_FOUND)

        setattr(songlist, f'song{slot}', None)
        songlist.save(update_fields=[f'song{slot}'])

        is_song_used_elsewhere = SongList.objects.filter(
            Q(song1=song) | Q(song2=song) | Q(song3=song) | Q(song4=song) | Q(song5=song)
        ).exists()

        if not is_song_used_elsewhere:
            song.delete()

        songlist.refresh_from_db()
        current_count = sum(
            1
            for slot_song in [songlist.song1, songlist.song2, songlist.song3, songlist.song4, songlist.song5]
            if slot_song is not None
        )

        return Response(
            {
                'detail': 'Musica removida com sucesso.',
                'count': current_count,
                'missing': max(0, 5 - current_count),
                'is_complete': current_count == 5,
            },
            status=status.HTTP_200_OK,
        )
    