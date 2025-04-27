from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import os

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False  
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(os.path.abspath(os.path.dirname(__file__)), "events.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    time = db.Column(db.String(10), nullable=False)  # 🔥 Chuyển về kiểu chuỗi để tránh lỗi
    description = db.Column(db.String(500))
    location = db.Column(db.String(200))

    def to_dict(self):
        return {
            "id": self.id,
            "Tên sự kiện": self.title,
            "Ngày": self.date.strftime("%Y-%m-%d"),
            "Thời gian": self.time,  # 🔥 Giữ nguyên kiểu chuỗi, không cần `.strftime("%H:%M")`
            "Mô tả": self.description,
            "Địa điểm": self.location
        }

def convert_date_format(date_str):
    """ Chuyển đổi ngày từ 'DD/MM/YYYY' sang 'YYYY-MM-DD' """
    try:
        return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        return None  # Trả về None nếu không thể chuyển đổi

def import_json_to_db(json_file):
    """ Cập nhật database từ JSON, nếu sự kiện bị xóa khỏi JSON thì cũng xóa khỏi database """
    if not os.path.exists(json_file):
        print(f"❌ File '{json_file}' không tồn tại! Không có dữ liệu để cập nhật.")
        return
    
    with open(json_file, "r", encoding="utf-8") as file:
        json_events = json.load(file)

    with app.app_context():
        db_events = Event.query.all()
        db_event_titles = {event.title for event in db_events} 
        json_event_titles = {event["Tên sự kiện"] for event in json_events}  

        for event in db_events:
            if event.title not in json_event_titles:
                db.session.delete(event)
                print(f"🗑️ Xóa sự kiện: {event.title} vì không còn trong JSON!")

        for event in json_events:
            try:
                # 🔄 **Chuyển đổi định dạng ngày nếu cần**
                date = convert_date_format(event["Ngày"])
                if not date:
                    print(f"❌ Lỗi: Ngày không đúng định dạng trong sự kiện '{event['Tên sự kiện']}'")
                    continue
                
                time_str = event.get("Thời gian", "00:00")

                existing_event = Event.query.filter_by(title=event["Tên sự kiện"], date=date).first()
                if existing_event:
                    existing_event.time = time_str
                    existing_event.description = event.get("Mô tả", "Không có mô tả")
                    existing_event.location = event.get("Địa điểm", "Không có địa điểm")
                    print(f"🔄 Cập nhật sự kiện: {event['Tên sự kiện']}")
                else:
                    new_event = Event(
                        title=event["Tên sự kiện"],
                        date=datetime.strptime(date, "%Y-%m-%d"),
                        time=time_str,
                        description=event.get("Mô tả", "Không có mô tả"),
                        location=event.get("Địa điểm", "Không có địa điểm")
                    )
                    db.session.add(new_event)
                    print(f"✅ Thêm mới sự kiện: {event['Tên sự kiện']}")

            except Exception as e:
                print(f"❌ Lỗi format dữ liệu trong sự kiện: {event} - {e}")

        db.session.commit()
        print("✅ Hoàn tất cập nhật dữ liệu từ JSON vào database!")



with app.app_context():
    db.create_all()
    import_json_to_db("events.json") 

@app.route("/events", methods=["GET"])
def get_events():
    events = Event.query.all()
    return jsonify([event.to_dict() for event in events])

@app.route("/api/events/<int:event_id>", methods=["GET"])
def get_event(event_id):
    event = Event.query.get(event_id)
    if event:
        return jsonify(event.to_dict())
    else:
        return jsonify({"error": "Event not found"}), 404

@app.route("/api/events", methods=["POST"])
def add_event():
    try:
        if request.content_type != "application/json":  
            return jsonify({"error": "Invalid content type, expected JSON"}), 400

        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400

        # Kiểm tra nếu dữ liệu là danh sách sự kiện
        if isinstance(data, list):  
            for event in data:
                add_single_event(event)  # Thêm từng sự kiện vào database
            db.session.commit()  # Lưu thay đổi vào database
            return jsonify({"message": "Events added successfully!"}), 201

        # Nếu chỉ có một sự kiện gửi lên
        add_single_event(data)
        db.session.commit()
        return jsonify({"message": "Event added successfully!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def add_single_event(data):
    """ Hàm đơn giản để thêm một sự kiện vào database """
    title = data.get("Tên sự kiện")
    date_str = data.get("Ngày")
    time_str = data.get("Thời gian", "")
    description = data.get("Mô tả", "")
    location = data.get("Địa điểm", "")

    if not title or not date_str or not time_str:
        return  

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return  

    new_event = Event(
        title=title,
        date=date,
        time=time_str,
        description=description,
        location=location
    )
    db.session.add(new_event)


@app.route("/api/events/<int:event_id>", methods=["PUT"])
def update_event(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404
    try:
        if request.content_type == "application/json":
            data = request.get_json()
            if not data:
                return jsonify({"error": "No JSON data received"}), 400
        else:
            return jsonify({"error": "Invalid content type"}), 400

        title = data.get("Tên sự kiện")
        date_str = data.get("Ngày")
        time_str = data.get("Thời gian")
        description = data.get("Mô tả")
        location = data.get("Địa điểm")

        if not title or not date_str or not time_str:
            return jsonify({"error": "Title, Date, and Time are required"}), 400  # 🔥 Đảm bảo 'Time' là bắt buộc

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Invalid date format. Use 'YYYY-MM-DD'"}), 400

        event.title = title
        event.date = date
        event.time = time_str
        event.description = description
        event.location = location

        db.session.commit()
        return jsonify({"message": "Event updated successfully!", **event.to_dict()})  # 🔥 Bỏ key "event"
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/events/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404
    try:
        db.session.delete(event)
        db.session.commit()
        return jsonify({"message": "Event deleted successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
