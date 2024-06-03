
import traceback

from flask import Flask, request, redirect, jsonify, render_template

from config import secert, server_port
from card_data_lite import CardData

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)



@app.before_request
def before_request_func():
    if request.path == '/health':
        return None  # 跳过'/check_secert'端点的校验
    if request.path == '/':
        return None  # 跳过'/check_secert'端点的校验
    if request.path == '/about':
        return None  # 跳过'/check_secert'端点的校验
    return  None
    secert_h = request.headers.get('secert_h')
    if secert_h != secert:
        return jsonify({"code": 0, "message": "Invalid secert_h"}), 403

@app.route('/')
def main():
    return render_template('welcome.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/list_all_users')
def list_all_users():
    # 创建 FaceData 实例并获取所有用户信息
    face_data = CardData()
    users = face_data.list_all_user()

    del face_data  # 在函数结束时关闭数据库连接
    return render_template('list_users.html', users=users)


#有用，定义support为card的
@app.route('/list_all_card',methods=['GET'])
def list_all_card():
    # 创建 FaceData 实例并获取所有用户信息
    face_data = CardData()
    users = face_data.list_all_user()
    del face_data  # 在函数结束时关闭数据库连接
    user_list = []
    for user in users:
        user_dict = {
            'student_id': user[1],
            'username': user[2],
            'card_id': user[0]
        }
        user_list.append(user_dict)
    return jsonify(user_list)




@app.route('/sync_upload', methods=['POST'])
def sync_upload():
    # Check if a valid image file was uploaded
    if request.method == 'POST':
        facedata = CardData()

        data = request.get_json()
        card_data = data["data"]
        if data["model"] == 'ADD':
            # 逐条处理就行
            for i in card_data:
                if facedata.exists_user(i["student_id"]):
                    if i["is_none"] == True:
                        # 为空还存在用户，按照规则需要也同步为空,暂时只支持卡号一种，删除该条数据即可!
                        facedata.cursor.execute("DELETE FROM user WHERE student_id = ?",(i["student_id"],))
                    else:
                        # 需要更新人脸数据
                        facedata.cursor.execute("UPDATE user SET card_id = ? WHERE student_id = ?",(i["card_id"],i["student_id"]))
                else:
                    # 用户不存在，只考虑是否需要新增
                    if i["is_none"] == False:
                        facedata.cursor.execute("INSERT INTO user (card_id,student_id,username) values (?,?,?)",(i["card_id"],i["student_id"],i["username"]))
            facedata.conn.commit()
            return jsonify({"code":1,"msg":"增量同步成功"})

        elif data["model"] == 'NEW':
            facedata.cursor.execute("DELETE FROM user")
            for i in card_data:
                if i["is_none"] == False:
                    facedata.cursor.execute("INSERT INTO user (card_id,student_id,username) values (?,?,?)",
                                            ( i["card_id"],i["student_id"], i["username"]))
            facedata.conn.commit()
            return jsonify({"code":1,"msg":"全新同步成功"})
        else:
            return jsonify({"code":0,"msg":"model异常"})

    return jsonify({"code":0,"msg":"请用POST请求"})
@app.route('/update_images', methods=['GET', 'POST'])
def upload_new_image():
    # Check if a valid image file was uploaded
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']
        user_name = request.form.get('username')
        student_id = request.form.get('student_id')
        face_id = request.form.get('face_id')

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # The image file seems valid! Detect faces and return the result.
            return jsonify({})

    # If no valid image file was uploaded, show the file upload form:
    return render_template('update_images.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




@app.route('/get', methods=['GET', 'POST'])
def get_user_info():
    if request.method == 'GET':
        return render_template('get.html')

    if request.method == 'POST':
        # 从请求中获取要查询的学生ID
        # request.args.get('student_id')
        student_id = request.json.get('student_id')

        print("Received GET request for student ID:", student_id)  # 添加调试语句

        if student_id:
            try:
                # 创建 FaceData 实例并获取用户信息
                face_data = CardData()
                user_info = face_data.get_user_info(student_id)
                del face_data  # 在函数结束时关闭数据库连接

                if user_info:
                    return jsonify({'user_info': user_info})
                else:
                    return jsonify({'error': 'User not found'})
            except Exception as e:
                print("An error occurred:", e)  # 添加调试语句
                traceback.print_exc()  # 添加调试语句
                return jsonify({'error': 'An internal server error occurred'})
        else:
            # 如果没有提供学生ID，返回一个页面提醒用户输入学生ID
            return render_template('list_users.html')
    # 如果是 POST 请求，直接返回页面


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'GET':
        return render_template('add.html')

    if request.method == 'POST':
        student_id = request.json.get('student_id')
        username = request.json.get('username')
        card_id = request.json.get('card_id')
        if student_id and username and card_id:
            face_data = CardData()
            face_data.create_user(student_id, username,card_id)
            del face_data  # 在函数结束时关闭数据库连接
            return jsonify({'message': 'User added successfully'})
        else:
            return jsonify({'error': 'Missing student_id or username'})


@app.route('/delete', methods=['GET', 'POST'])
def delete():
    if request.method == 'POST':
        student_id = request.form.get('studentID')  # 从请求中获取要删除的学生ID

        if not student_id:
            return jsonify({'error': '缺少studentID参数'}), 400  # 检查学生ID是否为空

        face_data = CardData()  # 创建 FaceData 实例
        deleted = face_data.delete_user(student_id)  # 删除用户信息并接收操作结果
        del face_data  # 关闭数据库连接

        if deleted:
            return jsonify({'message': '成功删除用户信息'})  # 如果删除成功，返回成功消息
        else:
            return jsonify({'error': '未找到要删除的用户'})  # 如果没有找到用户，返回错误消息

    return render_template('delete.html')  # 如果是 GET 请求，返回删除页面


@app.route('/revise', methods=['POST', 'GET'])
def revise():
    if request.method == 'POST':
        student_id = request.form.get('studentID')  # 获取学生ID
        student_name = request.form.get('studentName')  # 获取学生姓名

        # 检查学生ID和姓名是否都提供了
        if not student_id or not student_name:
            return jsonify({'error': '学生ID和姓名不能为空'}), 400

        face_data = CardData()  # 创建 FaceData 实例
        user_info = face_data.get_user_info(student_id)  # 获取学生当前信息

        if user_info:
            old_name = user_info[1]  # 获取更新前的学生姓名
            updated = face_data.update_user(student_id, student_name)  # 更新用户信息并接收操作结果

            if updated:
                # 返回成功更新的学生信息和更改前后信息
                return render_template('update_student_info.html', old_name=old_name, new_name=student_name)
            else:
                return jsonify({'error': '更新学生信息失败'}), 500
        else:
            return jsonify({'error': '未找到要更新的学生'}), 404

    return render_template('revise.html')  # 如果是 GET 请求，返回编辑页面


@app.route('/check_secert', methods=['GET'])
def check_secert():
    _secert = request.args.get("secert")
    if _secert != secert:
        return jsonify({"code": 0})
    return jsonify({"code": 1})


#
# @app.route('/new', methods=['GET', 'POST'])
# def upload_new_image():
#     # Check if a valid image file was uploaded
#     if request.method == 'POST':
#         if 'file' not in request.files:
#             return redirect(request.url)
#
#         file = request.files['file']
#         user_name = request.form.get('username')
#         student_id = request.form.get('student_id')
#         face_id = request.form.get('face_id')
#
#         if file.filename == '':
#             return redirect(request.url)
#
#         if file and allowed_file(file.filename):
#             # The image file seems valid! Detect faces and return the result.
#             return jsonify(add_new_faces_in_image(file, user_name, student_id, face_id))
#
#     # If no valid image file was uploaded, show the file upload form:
#     return '''
#    <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Camera Capture and Crop</title>
#     <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.12/cropper.min.css">
#     <style>
#         #preview {
#             width: 100%;
#             height: auto;
#             margin-top: 20px;
#         }
#     </style>
# </head>
# <body>
#
#          <form method="post" enctype="multipart/form-data">
#         <input type="file" name="file">
#         <input name="username" value="username">
#         <input name="student_id" value="student_id">
#         <input name="face_id" value="face_id">
#         <button type="submit">Upload File</button>
#     </form>
# </body>
# </html>
#
#     '''


@app.route('/health', methods=['GET'])
def health():
    return "服务存活"


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS






if __name__ == "__main__":
    app.run(host='0.0.0.0', port=server_port, debug=True)



