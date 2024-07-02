SELECT
CAD.schoolid,
CAD.date_value,
CAD.insession,
CAD.membershipvalue,
CAD.type,
CYD.letter as Cycle_Day,
BS.name as Bell_Schedule,
CAD.a as Track_A,
CAD.b as Track_B,
CAD.c as Track_C,
CAD.d as Track_D,
CAD.e as Track_E,
CAD.f as Track_F
FROM
calendar_day CAD
JOIN cycle_day CYD ON CAD.cycle_day_id = CYD.id
join bell_schedule BS on CAD.bell_schedule_id = BS.id
WHERE
--CAD.schoolid = ~(curschoolid) AND
CAD.date_value like sysdate