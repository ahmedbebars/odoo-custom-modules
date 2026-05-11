/** @odoo-module */
/**
 * Custom Planning — Gantt & Calendar Extensions
 */

// ===== Conflict Checker =====
export class ShiftConflictChecker {
    constructor(shifts) {
        this.shifts = shifts;
    }

    checkConflict(resourceId, start, end) {
        return this.shifts.some(
            (s) =>
                s.resource_id === resourceId &&
                s.state !== "cancelled" &&
                new Date(s.start_datetime) < new Date(end) &&
                new Date(s.end_datetime) > new Date(start)
        );
    }

    getConflicts(resourceId) {
        const resourceShifts = this.shifts
            .filter((s) => s.resource_id === resourceId && s.state !== "cancelled")
            .sort((a, b) => new Date(a.start_datetime) - new Date(b.start_datetime));

        const conflicts = [];
        for (let i = 0; i < resourceShifts.length - 1; i++) {
            const curr = resourceShifts[i];
            const next = resourceShifts[i + 1];
            if (new Date(curr.end_datetime) > new Date(next.start_datetime)) {
                conflicts.push({ shift1: curr, shift2: next });
            }
        }
        return conflicts;
    }
}

// ===== Hours Calculator =====
export class PlanningHoursCalc {
    static getHours(startDatetime, endDatetime) {
        const diff = new Date(endDatetime) - new Date(startDatetime);
        return diff / (1000 * 60 * 60);
    }

    static formatHours(hours) {
        const h = Math.floor(hours);
        const m = Math.round((hours - h) * 60);
        return `${h}:${m.toString().padStart(2, "0")}`;
    }

    static getWeeklyHours(shifts, resourceId) {
        const now = new Date();
        const startOfWeek = new Date(now);
        startOfWeek.setDate(now.getDate() - now.getDay());

        return shifts
            .filter(
                (s) =>
                    s.resource_id === resourceId &&
                    s.state !== "cancelled" &&
                    new Date(s.start_datetime) >= startOfWeek
            )
            .reduce(
                (total, s) => total + this.getHours(s.start_datetime, s.end_datetime),
                0
            );
    }
}

// ===== Auto Plan Simulator =====
export class AutoPlanSimulator {
    constructor(openShifts, resources) {
        this.openShifts = openShifts;
        this.resources = resources;
        this.assignments = [];
    }

    simulate() {
        const checker = new ShiftConflictChecker(this.assignments);

        for (const shift of this.openShifts) {
            const eligible = this.resources.filter((r) => {
                if (shift.role_id) {
                    return r.role_ids && r.role_ids.includes(shift.role_id);
                }
                return true;
            });

            for (const resource of eligible) {
                if (!checker.checkConflict(resource.id, shift.start_datetime, shift.end_datetime)) {
                    const assignment = { ...shift, resource_id: resource.id };
                    this.assignments.push(assignment);
                    break;
                }
            }
        }

        return {
            assigned: this.assignments.length,
            total: this.openShifts.length,
            unassigned: this.openShifts.length - this.assignments.length,
        };
    }
}

export default { ShiftConflictChecker, PlanningHoursCalc, AutoPlanSimulator };
