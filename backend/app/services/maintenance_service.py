from sqlalchemy import func

from app.extensions import db
from app.models import (
    Elevator,
    FaultReport,
    InspectionRecord,
    INSPECTION_RESULT_NORMAL,
    INSPECTION_RESULT_SEVERE,
    INSPECTION_RESULT_SLIGHT,
    INSPECTION_RESULTS,
    INSPECTION_HANDLING_PLANS,
    MaintenancePlan,
    parse_date,
    SEVERE_INSPECTION_RESULTS,
)
from app.repositories.base import commit


class FieldValidationError(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors
        super().__init__("Validation failed")


def list_plans():
    plans = MaintenancePlan.query.order_by(MaintenancePlan.scheduled_date.asc()).all()
    return [item.to_dict() for item in plans]


def create_plan(payload):
    plan = MaintenancePlan(
        title=payload["title"],
        plan_type=payload["planType"],
        scheduled_date=parse_date(payload["scheduledDate"]),
        assignee=payload["assignee"],
        status=payload.get("status", "Pending"),
        notes=payload.get("notes", ""),
        elevator_id=payload["elevatorId"],
    )
    return commit(plan).to_dict()


def update_plan(plan_id, payload):
    plan = MaintenancePlan.query.get_or_404(plan_id)
    for field, attr in {
        "title": "title",
        "planType": "plan_type",
        "scheduledDate": "scheduled_date",
        "assignee": "assignee",
        "status": "status",
        "notes": "notes",
        "elevatorId": "elevator_id",
    }.items():
        if field in payload:
            value = parse_date(payload[field]) if field == "scheduledDate" else payload[field]
            setattr(plan, attr, value)
    db.session.commit()
    return plan.to_dict()


def list_inspections():
    records = InspectionRecord.query.order_by(InspectionRecord.inspected_at.desc()).all()
    return [item.to_dict() for item in records]


def validate_inspection_payload(payload):
    errors = {}

    if not payload.get("inspector") or not str(payload["inspector"]).strip():
        errors["inspector"] = "请填写巡检员姓名"
    if not payload.get("checklist") or not str(payload["checklist"]).strip():
        errors["checklist"] = "请填写检查项内容"
    if not payload.get("elevatorId"):
        errors["elevatorId"] = "请选择电梯"
    else:
        elevator = Elevator.query.get(payload["elevatorId"])
        if not elevator:
            errors["elevatorId"] = "选择的电梯不存在"
    if not payload.get("result"):
        errors["result"] = "请选择巡检结果"
    elif payload["result"] not in INSPECTION_RESULTS:
        errors["result"] = "无效的巡检结果"
    if payload.get("result") in SEVERE_INSPECTION_RESULTS:
        if not payload.get("problemDescription") or not str(payload["problemDescription"]).strip():
            errors["problemDescription"] = "严重异常必须填写问题描述"

    if errors:
        raise FieldValidationError(errors)


def create_inspection(payload):
    validate_inspection_payload(payload)

    record = InspectionRecord(
        inspector=payload["inspector"].strip(),
        result=payload["result"],
        checklist=payload["checklist"].strip(),
        attachment_url=payload.get("attachmentUrl", ""),
        elevator_id=payload["elevatorId"],
    )
    record = commit(record)

    created_fault = None
    if record.result in SEVERE_INSPECTION_RESULTS:
        problem_desc = payload.get("problemDescription", "").strip()
        fault = FaultReport(
            reporter=record.inspector,
            phone="",
            fault_type="巡检发现严重异常",
            description=problem_desc,
            priority="Urgent",
            status="Pending",
            elevator_id=record.elevator_id,
        )
        created_fault = commit(fault).to_dict()

    result = record.to_dict()
    if created_fault:
        result["createdFault"] = created_fault
    return result


def inspection_statistics():
    result_counts = dict(
        db.session.query(InspectionRecord.result, func.count(InspectionRecord.id))
        .group_by(InspectionRecord.result)
        .all()
    )
    return {
        "totalInspections": InspectionRecord.query.count(),
        "normalCount": result_counts.get(INSPECTION_RESULT_NORMAL, 0),
        "slightAbnormalCount": result_counts.get(INSPECTION_RESULT_SLIGHT, 0),
        "severeAbnormalCount": result_counts.get(INSPECTION_RESULT_SEVERE, 0),
        "resultCounts": result_counts,
        "handlingPlans": INSPECTION_HANDLING_PLANS,
    }
