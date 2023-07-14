import io
import zipfile
import tensorflow as tf
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import FileResponse, HttpResponse
import pandas as pd
import os
import sys

script_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_path)
from books.graduate.main import Graduate, IR_problem
from books.graduate.test import create_img_env, dump_zip, add_directory_to_zip

g = Graduate()
p = IR_problem()
ans = p.get_answer("心脏病是由什么所导致的")

print(ans)


def clear_session():
    tf.keras.backend.clear_session()


class GetFile(APIView):
    def post(self, request):
        print("-----UPLOAD-SUCCEED-----")
        answer = self.handle_file(request)
        return answer

    def handle_file(self, request):
        file = request.FILES.get('file', None)
        filename = request.GET.get('filename', None)
        # print(filename)
        print(file)
        file_path = os.path.join(script_path, "../files", filename)
        with open(file_path, "wb") as f:
            for chunk in file.chunks():
                f.write(chunk)
        clear_session()
        g.orc(file_path)
        clear_session()
        return Response("Succeed!")


class ZipFile(APIView):
    def get(self, request):
        print("-----GET-ZIP-FILE-----")
        if not g.pdf:
            return Response("Couldn't get the pdf filepath", status=404)
        if not g.extract_zip_path:
            return Response("Couldn't find the zip filepath", status=404)
        zip_stream = io.BytesIO()
        file_path = g.extract_zip_path
        draw_path = g.draw_picture_path
        # get the file name
        file_name = file_path.split("\\")[-1].split("/")[-1]
        file_name = file_path[:-4]
        # create the folder and dump
        folder_path = create_img_env(pdf_name=file_name)
        dump_zip(file_path, folder_path)
        # print("file_path is:")
        # print(file_path)
        # print("folder_path is:")
        # print(folder_path)
        # print("draw_path is:")
        # print(draw_path)
        # do zip process
        with zipfile.ZipFile(zip_stream, 'w') as zip_data:
            add_directory_to_zip(zip_data, folder_path)
            add_directory_to_zip(zip_data, draw_path)
        response = HttpResponse(content_type='application/zip')
        # Set the content disposition header to force browser download
        response['Content-Disposition'] = 'attachment; filename=files.zip'
        # Write the zip file data to the response
        response.write(zip_stream.getvalue())
        zip_stream.close()

        return response


class DrawFile(APIView):
    def get(self, response):
        print("-----GET-PICTURES-----")
        if not g.pdf:
            return Response("Couldn't get the pdf filepath", status=404)
        if not g.draw_picture_path:
            return Response("Couldn't find the picture filepath", status=404)
        image_path = g.draw_picture_path
        if os.path.exists(image_path):
            image_file = open(image_path, "rb")
            return FileResponse(image_file)
        else:
            return Response(status=404)


class ExcelFile(APIView):
    def get(self, response):
        print("-----GET-EXCEL-----")
        if not g.pdf:
            return Response("Couldn't get the pdf filepath", status=404)
        if not g.dump_excel_path:
            return Response("Couldn't find the excel filepath", status=404)
        excel_file_path = g.dump_excel_path
        print(excel_file_path)
        # Open the Excel file and read it as binary data
        df = pd.read_excel(excel_file_path)
        # Create an in-memory buffer for the new Excel file
        excel_buffer = io.BytesIO()
        # Write the DataFrame to the buffer as an Excel file
        df.to_excel(excel_buffer, index=False)
        # Set the buffer's pointer to the beginning of the file
        excel_buffer.seek(0)
        # Create a new HTTP response object with the Excel file data
        response = Response(excel_buffer.read(),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={os.path.basename(excel_file_path)}'
        return response


class ExtractFile(APIView):
    def get(self, request):
        clear_session()
        g.IE_process()
        clear_session()
        return Response(g.extract_triples)


class QueryFile(APIView):
    def get(self, request):
        question = request.GET.get('question')
        clear_session()
        answer = p.get_answer(question)
        # answer = g.get_answer(question)
        clear_session()
        return Response(answer)


class ClearAction(APIView):
    def get(self, request):
        clear_session()
        g.clear()
        return Response("Clear-OK!")