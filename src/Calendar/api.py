# from rest_framework import generics
# from rest_framework.response import Response
#
# from .serializers import RegisterSerializer, UserSerializer
#
#
# class RegisterApi(generics.GenericAPIView):
#     serializer_class = RegisterSerializer
#
#     def post(self, request, *args, **kwargs):
#         #register ser
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         print(request.data)
#         user = serializer.save()
#         return Response({
#             "user": UserSerializer(user, context=self.get_serializer_context()).data,
#             "message": "User created",
#         })
