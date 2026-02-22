🧱 STEP 1 — Backend API

📁 File: routes/customer_routes.py

📍 Add:

@app.route("/api/customer/applications", methods=["GET"])
@role_required("customer")
def get_customer_applications():

    user_id = get_jwt_identity()

    apps = db.session.execute(text("""
        SELECT a.id,
               ss.service_name,
               a.status,
               p.status AS payment_status,
               a.mode,
               a.created_at
        FROM applications a
        JOIN state_services ss ON a.state_service_id = ss.id
        LEFT JOIN payments p ON p.application_id = a.id
        WHERE a.user_id = :user
        ORDER BY a.created_at DESC
    """), {"user": user_id}).fetchall()

    result = []
    for a in apps:
        result.append({
            "id": str(a.id),
            "service_name": a.service_name,
            "status": a.status,
            "payment_status": a.payment_status,
            "mode": a.mode,
            "created_at": a.created_at
        })

    return result
