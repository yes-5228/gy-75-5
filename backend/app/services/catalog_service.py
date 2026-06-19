from app.models import Community, Elevator, INSPECTION_HANDLING_PLANS, InspectionRecord


def list_communities():
    return [item.to_dict() for item in Community.query.order_by(Community.name).all()]


def list_elevators():
    elevators = Elevator.query.order_by(Elevator.code).all()
    result = []
    for elevator in elevators:
        data = elevator.to_dict()
        latest_inspection = (
            InspectionRecord.query.filter_by(elevator_id=elevator.id)
            .order_by(InspectionRecord.inspected_at.desc())
            .first()
        )
        if latest_inspection:
            data["latestInspectionResult"] = latest_inspection.result
            data["latestInspectionAt"] = latest_inspection.inspected_at.isoformat(timespec="minutes")
            data["inspectionHandlingPlan"] = INSPECTION_HANDLING_PLANS.get(latest_inspection.result, "")
        else:
            data["latestInspectionResult"] = None
            data["latestInspectionAt"] = None
            data["inspectionHandlingPlan"] = ""
        result.append(data)
    return result
