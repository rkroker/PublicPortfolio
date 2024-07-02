SELECT
	crs.coursesdcid,
	core.course_number,
	core.course_name,
	crs.advanced_placement_tf
FROM
	s_pa_crs_x crs
	join courses core on core.dcid = crs.coursesdcid
WHERE
	crs.advanced_placement_tf = 1
