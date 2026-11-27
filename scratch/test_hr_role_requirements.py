import urllib.request
import json
import sys

BASE_URL = "http://localhost:8080/api"

def login(email, password):
    data = json.dumps({"email": email, "password": password}).encode("utf-8")
    req = urllib.request.Request(f"{BASE_URL}/auth/login", data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        body = json.loads(resp.read().decode("utf-8"))
        return body["token"]

def api_call(token, method, endpoint, payload=None):
    url = f"{BASE_URL}{endpoint}"
    data = json.dumps(payload).encode("utf-8") if payload else None
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))

def main():
    print("=== 1. AUTHENTICATING AS HR SPECIALIST ===")
    token = login("hr.test@infosys.com", "Password@123")
    print(f"[PASS] Logged in as HR, token received ({len(token)} chars)")

    print("\n=== 2. TESTING GET /api/hr/roles ===")
    status, roles = api_call(token, "GET", "/hr/roles")
    assert status == 200, f"Expected 200, got {status}"
    assert isinstance(roles, list), "Expected list of roles"
    print(f"[PASS] Successfully retrieved {len(roles)} target roles without database error!")
    for r in roles[:3]:
        print(f"       Role: {r.get('roleName')} (ID: {r.get('roleId')})")
        print(f"       - Skills count: {len(r.get('skills', []))}")
        for sk in r.get("skills", [])[:2]:
            print(f"         * {sk.get('skillName')} | Req Level: {sk.get('requiredLevel')} | Weight: {sk.get('weightPct')}%")

    print("\n=== 3. TESTING CREATE TARGET ROLE (POST /api/hr/roles) ===")
    test_role_name = "QA Automation Lead (Test)"
    status, create_res = api_call(token, "POST", "/hr/roles", {
        "roleName": test_role_name,
        "description": "Leads test automation engineering cohorts"
    })
    assert status == 200, "Role creation should succeed"
    new_role_id = create_res.get("roleId")
    assert new_role_id, "New roleId should be returned"
    print(f"[PASS] Created target role ID: {new_role_id}")

    print("\n=== 4. TESTING ADD SKILL REQUIREMENT (POST /api/hr/roles/{id}/skills) ===")
    status, skill_res = api_call(token, "POST", f"/hr/roles/{new_role_id}/skills", {
        "skillId": 1,
        "requiredLevel": 4,
        "weightPct": 35
    })
    assert status == 200
    print(f"[PASS] Mapped Skill ID 1 to role with Level 4, 35% weight: {skill_res.get('message')}")

    # Verify retrieval
    _, updated_roles = api_call(token, "GET", "/hr/roles")
    matched = next((r for r in updated_roles if r.get("roleId") == new_role_id), None)
    assert matched, "Created role should appear in list"
    assert len(matched["skills"]) == 1, "Should have 1 mapped skill"
    assert matched["skills"][0]["requiredLevel"] == 4, "Required level should be 4"
    assert matched["skills"][0]["weightPct"] == 35, "Weight should be 35%"
    print(f"[PASS] Verified persistence of skill requirement: Level {matched['skills'][0]['requiredLevel']}, Weight {matched['skills'][0]['weightPct']}%")

    print("\n=== 5. TESTING UPDATE SKILL REQUIREMENT (PUT /api/hr/roles/{id}/skills/{skillId}) ===")
    status, update_skill_res = api_call(token, "PUT", f"/hr/roles/{new_role_id}/skills/1", {
        "requiredLevel": 5,
        "weightPct": 50
    })
    assert status == 200
    print(f"[PASS] Updated skill requirement: {update_skill_res.get('message')}")

    # Verify updated values
    _, updated_roles2 = api_call(token, "GET", "/hr/roles")
    matched2 = next((r for r in updated_roles2 if r.get("roleId") == new_role_id), None)
    assert matched2["skills"][0]["requiredLevel"] == 5, "Required level should now be 5"
    assert matched2["skills"][0]["weightPct"] == 50, "Weight should now be 50%"
    print(f"[PASS] Verified updated skill requirement: Level {matched2['skills'][0]['requiredLevel']}, Weight {matched2['skills'][0]['weightPct']}%")

    print("\n=== 6. TESTING UPDATE ROLE DETAILS (PUT /api/hr/roles/{id}) ===")
    status, update_role_res = api_call(token, "PUT", f"/hr/roles/{new_role_id}", {
        "roleName": "Senior QA Automation Lead (Test)",
        "description": "Updated purpose and scope"
    })
    assert status == 200
    print(f"[PASS] Updated role details: {update_role_res.get('message')}")

    print("\n=== 7. TESTING DELETE SKILL REQUIREMENT (DELETE /api/hr/roles/{id}/skills/{skillId}) ===")
    status, del_sk_res = api_call(token, "DELETE", f"/hr/roles/{new_role_id}/skills/1")
    assert status == 200
    print(f"[PASS] Removed skill from role: {del_sk_res.get('message')}")
    _, updated_roles3 = api_call(token, "GET", "/hr/roles")
    matched3 = next((r for r in updated_roles3 if r.get("roleId") == new_role_id), None)
    assert len(matched3["skills"]) == 0, "Mapped skills should now be 0"
    print("[PASS] Verified skill requirement removed")

    print("\n=== 8. TESTING DELETE TARGET ROLE (DELETE /api/hr/roles/{id}) ===")
    status, del_role_res = api_call(token, "DELETE", f"/hr/roles/{new_role_id}")
    assert status == 200
    print(f"[PASS] Deleted target role: {del_role_res.get('message')}")
    _, updated_roles4 = api_call(token, "GET", "/hr/roles")
    assert not any(r.get("roleId") == new_role_id for r in updated_roles4), "Role should no longer exist"
    print("[PASS] Verified target role deleted cleanly")

    print("\n=== 9. VERIFYING UNRELATED DASHBOARD MODULES (NO REGRESSION) ===")
    emp_token = login("emp.test@infosys.com", "Password@123")
    emp_status, emp_gaps = api_call(emp_token, "GET", "/employee/me/gaps")
    assert emp_status == 200
    print(f"[PASS] Employee dashboard /me/gaps returned HTTP 200")

    emp_roles_status, emp_roles = api_call(emp_token, "GET", "/employee/me/job-roles")
    assert emp_roles_status == 200
    print(f"[PASS] Employee role assessments /me/job-roles returned HTTP 200 ({len(emp_roles.get('roles', []))} roles)")

    print("\nALL VERIFICATIONS PASSED WITH ZERO ERRORS!")

if __name__ == "__main__":
    main()
