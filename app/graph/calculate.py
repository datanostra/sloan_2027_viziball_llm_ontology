#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
import os
import time
import app.util as util
import app.graph.util as gu
import app.graph.connector as gc


BATCH_SIZE = 500


def get_percentage_statistics_formula():
	"""
	Function to get percentage statistics formula.
	"""
	return {
		"fgp": {
			"row": "r.fga AS FGA, r.fg AS FG", 
			"formula": "CASE WHEN sum(FGA) <> 0 THEN 100 * (sum(FG) / sum(FGA)) ELSE 0 END"}, 
		"ftp": {
			"row": "r.fta AS FTA, r.ft AS FT", 
			"formula": "CASE WHEN sum(FTA) <> 0 THEN 100 * (sum(FT) / sum(FTA)) ELSE 0 END"}, 
		"tpp": {
			"row": "r.tpa AS TPA, r.tp AS TP", 
			"formula": "CASE WHEN sum(TPA) <> 0 THEN 100 * (sum(TP) / sum(TPA)) ELSE 0 END"}, 
		"tsp": {
			"row": "r.fga AS FGA, r.fta AS FTA, r.pts AS PTS", 
			"formula": "CASE WHEN sum(FGA) <> 0 OR sum(FTA) <> 0 THEN 100 * (sum(PTS) / (2*(sum(FGA) + (0.44 * sum(FTA))))) ELSE 0 END"}, 
		"orbp": {
			"row": "r.orb AS ORB, r.drb AS DRB", 
			"formula": "CASE WHEN sum(ORB) + sum(DRB) <> 0 THEN 100 * (sum(ORB) / (sum(ORB) + sum(DRB))) ELSE 0 END"}, 
		"drbp": {
			"row": "r.drb AS DRB, r.orb AS ORB", 
			"formula": "CASE WHEN sum(DRB) + sum(ORB) <> 0 THEN 100 * (sum(DRB) / (sum(DRB) + sum(ORB))) ELSE 0 END"}, 
		"efgp": {
			"row": "r.fga AS FGA, r.fg AS FG, r.tp AS TP", 
			"formula": "CASE WHEN sum(FGA) <> 0 THEN 100 * ((sum(FG) + (0.5 * sum(TP))) / sum(FGA)) ELSE 0 END"}, 
		"afgp": {
			"row": "r.fg AS FG, r.ast AS AST", 
			"formula": "CASE WHEN sum(FG) <> 0 THEN 100 * (sum(AST) / sum(FG)) ELSE 0 END"}, 
		"twpp": {
			"row": "r.twpa AS TWPA, r.twp AS TWP", 
			"formula": "CASE WHEN sum(TWPA) <> 0 THEN 100 * (sum(TWP) / sum(TWPA)) ELSE 0 END"}
	}


def adress():
	"""
	Calculate address on PLAYS relation.
	"""
	return "r.ads = (r.efgp + r.tsp) / 2"


def collective():
	"""
	Calculate collective on PLAYS relation.
	"""
	return "r.col = CASE WHEN r.fg <> 0 THEN (r.pr / r.fg) * 100 ELSE 0 END"


def aggressiveness():
	"""
	Calculate aggressiveness on PLAYS relation.
	"""
	return "r.agr = (r.blk + r.stl + r.pf) / $agrMax * 100"


def offensive_aggressiveness():
	"""
	Calculate offensive aggressiveness on PLAYS relation.
	"""
	return "r.oagr = (r.fc + r.orb) / $oagrMax * 100"


def altruism():
	"""
	Calculate altruism on PLAYS relation.
	"""
	return "r.alt = r.ast / $astMax * 100"


def usage():
	"""
	Calculate usage on PLAYS relation.
	"""
	return "r1.usg = CASE WHEN (r1.mp * (r2.fga + (0.44 * r2.fta) + r2.tov)) <> 0 THEN 100 * ((r1.fga + (0.44 * r1.fta) + r1.tov) * r2.mp) / (r1.mp * (r2.fga + (0.44 * r2.fta) + r2.tov)) ELSE 0 END"


def delta_plus_minus():
	"""
	Calculate delta plus-minus on PLAYS relation.
	"""
	return "r1.dpm = r1.pm - r2.dp"


def four_factors():
	"""
	Calculate four factors on PLAYS/BOXSCORE relation.
	"""
	return "r.ff = r.efgp * 0.4 + r.tur * 0.25 + r.orbp * 0.2 + r.ftr * 0.15"


def win_team():
	"""
	Calculate if the team win the match on BOXSCORE relation.
	"""
	return "r1.win = CASE WHEN r1.pts - r2.pts > 0 THEN 1 ELSE 0 END"


def win_player():
	"""
	Calculate if the player win the match on PLAYS relation.
	"""
	return "r1.win = CASE WHEN r2.win = 1 THEN 1 ELSE 0 END"


def assist_to_turnover():
	"""
	Calculate assist to turnover Ratio on PLAYS relation.
	"""
	return "r.att = CASE WHEN r.tov <> 0 THEN r.ast / r.tov ELSE r.ast END"


def field_goal():
	"""
	Calculate field goal percentage on PLAYS/BOXSCORE relation.
	"""
	return "r.fgp = CASE WHEN r.fga <> 0 THEN 100 * (r.fg / r.fga) ELSE 0 END"


def free_throw():
	"""
	Calculate free throw percentage on PLAYS/BOXSCORE relation.
	"""
	return "r.ftp = CASE WHEN r.fta <> 0 THEN 100 * (r.ft / r.fta) ELSE 0 END"


def three_points():
	"""
	Calculate three points percentage on PLAYS/BOXSCORE relation.
	"""
	return "r.tpp = CASE WHEN r.tpa <> 0 THEN 100 * (r.tp / r.tpa) ELSE 0 END"


def total_rebounds():
	"""
	Calculate total rebounds on PLAYS/BOXSCORE relation.
	"""
	return "r.tor = r.orb + r.drb"


def true_shooting():
	"""
	Calculate true shooting percentage on PLAYS/BOXSCORE relation.
	"""
	return "r.tsp = CASE WHEN r.fga <> 0 OR r.fta <> 0 THEN 100 * (r.pts / (2*(r.fga + (0.44 * r.fta)))) ELSE 0 END"


def possession():
	"""
	Calculate number of possesion on BOXSCORE relation.
	"""
	return "r.pos = r.fga + (0.44 * r.fta) + r.tov - r.orb"


def offensive_efficiency_team():
	"""
	Calculate offensive efficiency on BOXSCORE relation.
	"""
	return "r.oef = CASE WHEN r.pos <> 0 THEN 100 * (r.pts / r.pos) ELSE 0 END"


def defensive_efficiency_team():
	"""
	Calculate defensive efficiency on BOXSCORE relation.
	"""
	return "r1.def = CASE WHEN r2.pos <> 0 THEN 100 * (r2.pts / r2.pos) ELSE 0 END"


def offensive_rebound():
	"""
	Calculate offensive rebound percentage on BOXSCORE relation.
	"""
	return "r1.orbp = CASE WHEN r1.orb + r2.drb <> 0 THEN 100 * (r1.orb / (r1.orb + r2.drb)) ELSE 0 END"


def offensive_rebound_player():
	"""
	Calculate offensive rebound percentage on PLAYS relation.
	"""
	return "r1.orbp = CASE WHEN (r2.orb + r3.drb) <> 0 THEN 100 * (r1.orb / (r2.orb + r3.drb)) ELSE 0 END"


def defensive_rebound():
	"""
	Calculate defensive rebound percentage on BOXSCORE relation.
	"""
	return "r1.drbp = CASE WHEN (r1.drb + r2.orb) <> 0 THEN 100 * (r1.drb / (r1.drb + r2.orb)) ELSE 0 END"


def defensive_rebound_player():
	"""
	Calculate defensive rebound percentage on PLAYS relation.
	"""
	return "r1.drbp = CASE WHEN r2.drb + r3.orb <> 0 THEN 100 * (r1.drb / (r2.drb + r3.orb)) ELSE 0 END"


def effective_field_goal():
	"""
	Calculate effective field-goal percentage on PLAYS/BOXSCORE relation.
	"""
	return "r.efgp = CASE WHEN r.fga <> 0 THEN 100 * ((r.fg + (0.5 * r.tp)) / r.fga) ELSE 0 END"


def turnover_ratio():
	"""
	Calculate turnover ratio on PLAYS/BOXSCORE relation.
	"""
	return "r.tur = CASE WHEN (r.fga + (r.fta * 0.44) + r.ast + r.tov) <> 0 THEN (r.tov * 100) / (r.fga + (r.fta * 0.44) + r.ast + r.tov) ELSE 0 END"


def free_throw_rate():
	"""
	Calculate free throw rate on PLAYS/BOXSCORE relation.
	"""
	return "r.ftr = CASE WHEN r.fga <> 0 THEN 100 * (r.fta / r.fga) ELSE 0 END"


def assisted_points():
	"""
	Calculate assisted points percentage on BOXSCORE relation.
	"""
	return "r.afgp = CASE WHEN r.fg <> 0 THEN 100 * (r.ast / r.fg) ELSE 0 END"


def game_score():
	"""
	Calculate game score on PLAYS relation.
	"""
	return "r.gmsc = r.pts + (0.4 * r.fg) - (0.7 * r.fga) - (0.4 * (r.fta - r.ft)) + (0.7 * r.orb) + (0.3 * r.drb) + r.stl + (0.7 * r.ast) + (0.7 * r.blk) - (0.4 * r.pf) - r.tov"


def assist_ratio():
	"""
	Calculate assist ratio on BOXSCORE relation.
	"""
	return "r.astr = CASE WHEN (r.fga + (0.44 * r.fta) + r.ast + r.tov) <> 0 THEN r.ast / (r.fga + (0.44 * r.fta) + r.ast + r.tov) * 100 ELSE 0 END"


def two_points_stats():
	"""
	Calculate 2-pts & 2-pta on PLAYS/BOXSCORE relation.
	"""
	return "r.twp = r.fg - r.tp, r.twpa = r.fga - r.tpa"


def two_points_percentage():
	"""
	Calculate 2-ptp on PLAYS/BOXSCORE relation.
	"""
	return "r.twpp = CASE WHEN r.twpa <> 0 THEN 100 * (r.twp / r.twpa) ELSE 0 END"


def coach_game():
	"""
	Calculate jde for on PLAYS relation.
	"""
	return "r.jde = r.pm * 0.15 + r.twp * 2 + (r.twpa - r.twp) * -0.5 + r.tp * 3 + (r.tpa - r.tp) * -0.5 + r.ft * 1 + (r.fta - r.ft) * -0.5 + r.drb * 0.75 + r.orb * 1 + r.ast * 1 + r.stl * 2 + r.blk * 2 + r.tov * -0.75 + r.pf * -0.5"


def points_per_minute():
	"""
	Calculate points per minute on PLAYS relation.
	"""
	return "r.ppm = CASE WHEN r.mp > 0 THEN r.pts / r.mp ELSE 0 END"


def impact_per_minute():
	"""
	Calculate impact per minute on PLAYS relation.
	"""
	return "r1.piepm = CASE WHEN r1.mp > 0 THEN r1.pie / r1.mp ELSE 0 END"


def net_rating():
	"""
	Calculate net rating on PLAYS relation.
	"""
	return "r.nrt = r.oef - r.def"


def offensive_efficiency_player():
	"""
	Calculate offensive efficiency on PLAYS relation.
	"""
	qast = "(((r1.mp / (r2.mp / 5)) * (1.14 * ((r2.ast - r1.ast) / r2.fg))) + ((((r2.ast / r2.mp) * r1.mp * 5 - r1.ast) / ((r2.fg / r2.mp) * r1.mp * 5 - r1.fg)) * (1 - (r1.mp / (r2.mp / 5)))))"
	fgpart = "CASE WHEN r1.fga <> 0 THEN (r1.fg * (1 - 0.5 * ((r1.pts - r1.ft) / (2 * r1.fga)) * "+qast+")) ELSE 0 END"
	astpart = "(0.5 * (((r2.pts - r2.ft) - (r1.pts - r1.ft)) / (2 * (r2.fga - r1.fga))) * r1.ast)"
	ftpart = "CASE WHEN r1.fta <> 0 THEN ((1 - (1 - (r1.ft / r1.fta)) ^ 2) * 0.4 * r1.fta) ELSE 0 END"
	teamscoringposs = "(r2.fg + (1 - (1 - (r2.ft / r2.fta))^2) * r2.fta * 0.4)"
	teamplay = "("+teamscoringposs+" / (r2.fga + r2.fta * 0.4 + r2.tov))"
	teamorb = "(r2.orb / r2.orbp)"
	teamorbweight = "(((1 - "+teamorb+") * "+teamplay+") / ((1 - "+teamorb+") * "+teamplay+" +"+teamorb+" * (1 - "+teamplay +")))"
	orbpart = "(r1.orb * "+teamorbweight+" * "+teamplay+")"
	scposs = "(("+fgpart+" +"+astpart+" +"+ftpart+") * (1 - (r2.orb / "+teamscoringposs+") * "+teamorbweight+" * "+teamplay+") +"+orbpart+")"
	fgxposs = "((r1.fga - r1.fg) * (1 - 1.07 * "+teamorb+"))"
	ftxposs = "CASE WHEN r1.fta <> 0 THEN (((1 - (r1.ft / r1.fta))^2) * 0.4 * r1.fta) ELSE 0 END"
	totposs = "("+scposs+" +"+fgxposs+" +"+ftxposs+"+r1.tov)"
	pprodfgpart = "CASE WHEN r1.fga <> 0 THEN (2 * (r1.fg + 0.5 * r1.twp) * (1 - 0.5 * ((r1.pts - r1.ft) / (2 * r1.fga)) * "+qast+")) ELSE 0 END"
	pprodastpart = "(2 * ((r2.fg - r1.fg + 0.5 * (r2.twp - r1.twp)) / (r2.fg - r1.fg)) * 0.5 * (((r2.pts - r2.ft) - (r1.pts - r1.ft)) / (2 * (r2.fga - r1.fga))) * r1.ast)"
	pprodorbpart = "(r1.orb * "+teamorbweight+" * "+teamplay+" * (r2.pts / (r2.fg + (1 - (1 - (r2.ft / r2.fta))^2) * 0.4 * r2.fta)))"
	pprod = "(("+pprodfgpart+" +"+pprodastpart+" + r1.ft) * (1 - (r2.orb / "+teamscoringposs+") * "+teamorbweight+" * "+teamplay+") +"+pprodorbpart+")"
	return "r1.oef = CASE WHEN gds.util.isFinite("+pprod+"/"+totposs+") = true THEN 100 * ("+pprod+"/"+totposs+") ELSE 0 END"


def defensive_efficiency_player():
	"""
	Calculate defensive efficiency on PLAYS relation.
	"""
	dfg = "(FG / FGA)"
	dor = "(ORB / (ORB + r2.drb))"
	fmwt = "(("+dfg+" * (1 - "+dor+")) / ("+dfg+" * (1 - "+dor+" )+(1 - "+dfg+") * "+dor+"))"
	stops1 = "(r1.stl + r1.blk * "+fmwt+" * (1 - 1.07 * "+dor+") +  r1.drb * (1 - "+fmwt+"))"
	stops2 = "((((FGA - FG - r2.blk) / r2.mp) * "+fmwt+" * (1 - 1.07 * "+dor+") + ((TOV - r2.stl) / r2.mp)) * r1.mp + (PF / r2.pf) * 0.4 * FTA * (1 - (FT / FTA)) ^ 2)"
	stops = "("+stops1+" +"+stops2+")"
	stop = "(("+stops+" * MP) / (r2.pos * r1.mp))"
	teamdefensiverating = "(100 * (PTS / r2.pos))"
	dptsperscposs = "(PTS / (FG + (1 - (1 - (FT / FTA)) ^ 2) * FTA * 0.4))"
	drtg = teamdefensiverating+" + 0.2 * (100 * "+dptsperscposs+" * (1 - "+stop+") - "+teamdefensiverating+")"
	return "r1.def = CASE WHEN "+drtg+" <> 0 AND gds.util.isFinite("+drtg+") = true THEN "+drtg+" ELSE 0 END"


def set_advanced_statistics_team(logger, ctx, championship, list_games=None):
	"""
	Function to calculate teams advanced statistics.
	"""
	start_time = time.time()
	result_type = "single"
	
	# Calculate statistics on BOXSCORE relation
	check_gid = "WHERE g.gid IN $list_games " if list_games is not None else ""
	query = "CALL apoc.periodic.iterate('MATCH (:Team)-[r:BOXSCORE]->(g:Game) "+check_gid+"RETURN r', 'SET "+field_goal()+", "+free_throw()+", "+three_points()+", "+total_rebounds()+", "+true_shooting()+", "+possession()+", "+effective_field_goal()+", "+turnover_ratio()+", "+free_throw_rate()+", "+assisted_points()+", "+assist_ratio()+", "+two_points_stats()+"', {batchSize: $batchSize, params: {list_games: $list_games}})"
	
	result = gu.execute_query(logger, ctx, championship, result_type, query, batchSize=BATCH_SIZE, list_games=list_games)

	if result['failedOperations'] > 0:
		logger.warning("%s :: %s :: SET_BOXSCORE_FGP_FTP_TPP_TOR_TSP_POSS_OEF_EFGP_TUR_FTR_AGFP_ASTR_TWP_TWPA_TWPP :: %s :: %s", os.path.basename(__file__), os.getpid(), championship, result['failedOperations'])
	
	# Calculate statistics on BOXSCORE relation
	query = "CALL apoc.periodic.iterate('MATCH (:Team)-[r:BOXSCORE]->(g:Game) "+check_gid+"RETURN r', 'SET "+offensive_efficiency_team()+", "+two_points_percentage()+"', {batchSize: $batchSize, params: {list_games: $list_games}})"

	result = gu.execute_query(logger, ctx, championship, result_type, query, batchSize=BATCH_SIZE, list_games=list_games)

	if result['failedOperations'] > 0:
		logger.warning("%s :: %s :: SET_BOXSCORE_OEF_TWPP :: %s :: %s", os.path.basename(__file__), os.getpid(), championship, result['failedOperations'])


	# Calculate team impact estimate (TIE) on BOXSCORE relation
	# (GM = somme des BOXSCORE des deux équipes)
	query = "CALL apoc.periodic.iterate('MATCH (g:Game)<-[r1:BOXSCORE]-(:Team) "+check_gid+"RETURN g AS GAME, sum(r1.pts) AS GMPTS, sum(r1.fg) AS GMFG, sum(r1.ft) AS GMFT, sum(r1.fga) AS GMFGA, sum(r1.fta) AS GMFTA, sum(r1.drb) AS GMDRB, sum(r1.orb) AS GMORB, sum(r1.ast) AS GMAST, sum(r1.stl) AS GMSTL, sum(r1.blk) AS GMBLK, sum(r1.pf) AS GMPF, sum(r1.tov) AS GMTOV', 'MATCH (t:Team)-[r2:BOXSCORE]->(GAME) SET r2.tie = 100 * (r2.pts + r2.fg + r2.ft - r2.fga - r2.fta + r2.drb + (0.5 * r2.orb) + r2.ast + r2.stl + (0.5 * r2.blk) - r2.pf - r2.tov) / (GMPTS + GMFG + GMFT - GMFGA - GMFTA + GMDRB + (0.5 * GMORB) + GMAST + GMSTL + (0.5 * GMBLK) - GMPF - GMTOV)', {batchSize: $batchSize, params: {list_games: $list_games}})"

	result = gu.execute_query(logger, ctx, championship, result_type, query, batchSize=BATCH_SIZE, list_games=list_games)

	if result['failedOperations'] > 0:
		logger.warning("%s :: %s :: SET_BOXSCORE_TIE :: %s :: %s", os.path.basename(__file__), os.getpid(), championship, result['failedOperations'])

	# (r2 = BOXSCORE de l'autre équipe)
	check_gid = "WHERE g.gid IN $list_games AND t1.tid <> t2.tid " if list_games is not None else "WHERE t1.tid <> t2.tid "
	query = "CALL apoc.periodic.iterate('MATCH (t1:Team)-[r1:BOXSCORE]->(g:Game)<-[r2:BOXSCORE]-(t2:Team) "+check_gid+"RETURN r1, r2', 'SET "+offensive_rebound()+", "+defensive_rebound()+", "+defensive_efficiency_team()+", "+win_team()+"', {batchSize: $batchSize, params: {list_games: $list_games}})"

	result = gu.execute_query(logger, ctx, championship, result_type, query, batchSize=BATCH_SIZE, list_games=list_games)

	if result['failedOperations'] > 0:
		logger.warning("%s :: %s :: SET_BOXSCORE_ORBP_DRBP_DEF_WIN :: %s :: %s", os.path.basename(__file__), os.getpid(), championship, result['failedOperations'])

	# Calculate statistics on BOXSCORE relation
	check_gid = "WHERE g.gid IN $list_games " if list_games is not None else ""
	query = "CALL apoc.periodic.iterate('MATCH (:Team)-[r:BOXSCORE]->(g:Game) "+check_gid+"RETURN r', 'SET "+four_factors()+"', {batchSize: $batchSize, params: {list_games: $list_games}})"
	
	result = gu.execute_query(logger, ctx, championship, result_type, query, batchSize=BATCH_SIZE, list_games=list_games)

	if result['failedOperations'] > 0:
		logger.warning("%s :: %s :: SET_BOXSCORE_FF :: %s :: %s", os.path.basename(__file__), os.getpid(), championship, result['failedOperations'])
	
	# Calculate delta possession
	check_gid = "AND g.gid IN $list_games " if list_games is not None else ""
	query = "CALL apoc.periodic.iterate('MATCH (t:Team)-[r:BOXSCORE]->(g:Game)-[:BELONGS_TO]->(s:Season) WITH s.season AS season, t.tid AS tid, avg(r.pos) AS avgPos CALL apoc.cypher.run(\"MATCH (t:Team)-[r1:BOXSCORE]->(g:Game)<-[r2:BOXSCORE]-(:Team {tid: tid}) WHERE EXISTS((g)-[:BELONGS_TO]->(:Season {season: season})) "+check_gid+"RETURN r1, r2.pos AS pos\", {tid: tid, season: season, list_games: $list_games}) YIELD value RETURN value.r1 AS r1, value.pos AS pos, avgPos', 'SET r1.dpos = avgPos - pos', {batchSize: $batchSize, params: {list_games: $list_games}})"

	result = gu.execute_query(logger, ctx, championship, result_type, query, batchSize=BATCH_SIZE, list_games=list_games)

	if result['failedOperations'] > 0:
		logger.warning("%s :: %s :: SET_BOXSCORE_DPOS :: %s :: %s", os.path.basename(__file__), os.getpid(), championship, result['failedOperations'])
	
	# Calculate distance traveled for each match
	check_gid = "WHERE g.gid IN $list_games " if list_games is not None else ""
	query = "CALL apoc.periodic.iterate('MATCH (t1:Team)-[r:BOXSCORE]->(g:Game)<-[:BOXSCORE]-(t2:Team) "+check_gid+"RETURN r, g.dat AS d1, t1, CASE WHEN substring(g.gid, 9) = t1.shn THEN t1 ELSE t2 END AS t3','CALL (t1, d1) { OPTIONAL MATCH (t1)-[:BOXSCORE]->(g:Game)<-[:BOXSCORE]-(t2:Team) WHERE g.dat < d1 RETURN CASE WHEN substring(g.gid, 9) = t1.shn THEN t1 ELSE t2 END AS t4 ORDER BY g.dat DESC LIMIT 1 } SET r.dist = CASE WHEN t4 IS NULL THEN 0 ELSE point.distance(point({latitude: t3.lat, longitude: t3.long}), point({latitude: t4.lat, longitude: t4.long})) / 1000 END', {batchSize: $batchSize, params: {list_games: $list_games}})"

	result = gu.execute_query(logger, ctx, championship, result_type, query, batchSize=BATCH_SIZE, list_games=list_games)

	if result['failedOperations'] > 0:
		logger.warning("%s :: %s :: SET_BOXSCORE_DIST :: %s :: %s", os.path.basename(__file__), os.getpid(), championship, result['failedOperations'])
	
	# Calculate rest days for each match
	query = "CALL apoc.periodic.iterate('MATCH (t:Team)-[r:BOXSCORE]->(g:Game) "+check_gid+"RETURN t, r, g.dat AS d1','CALL (t, d1) { OPTIONAL MATCH (t)-[:BOXSCORE]->(g:Game) WHERE g.dat < d1 RETURN g.dat AS d2 ORDER BY d2 DESC LIMIT 1 } SET r.rd = CASE WHEN d2 IS NULL THEN -1 ELSE duration.inDays(date(toString(d2)), date(toString(d1))).days END', {batchSize: $batchSize, params: {list_games: $list_games}})"

	result = gu.execute_query(logger, ctx, championship, result_type, query, batchSize=BATCH_SIZE, list_games=list_games)

	if result['failedOperations'] > 0:
		logger.warning("%s :: %s :: SET_BOXSCORE_RD :: %s :: %s", os.path.basename(__file__), os.getpid(), championship, result['failedOperations'])
	
	# Reset rest days if null
	query = "MATCH (t:Team)-[r:BOXSCORE]->(g:Game) SET (CASE WHEN r.rd IS NULL THEN r END).rd = 0, (CASE WHEN r.dist IS NULL THEN r END).dist = 0"
	gu.execute_query(logger, ctx, championship, None, query, list_games=list_games)
	
	logger.info("%s :: %s :: SET_ADVANCED_STATISTICS_TEAM :: %s", os.path.basename(__file__), os.getpid(), util.get_duration(start_time))


def set_advanced_statistics_between_teams(logger, ctx, championship, list_games=None):
	"""
	Function to calculate advanced statistics between teams.
	"""
	start_time = time.time()
	result_type = "single"
	
	# Calculate net rating, pace factor, differential of points and points taken on BOXSCORE relation (r2 = BOXSCORE of other team).
	championships = gc.get_championships(logger, ctx)
	item = next((c for c in championships if c['shn'] == championship), None)
	check_gid = "WHERE g.gid IN $list_games " if list_games is not None else ""
	query = "CALL apoc.periodic.iterate('MATCH (g:Game)<-[r2:BOXSCORE]-(t:Team) "+check_gid+"RETURN g AS GAME, t.tid AS TID, r2.oef AS OEF, r2.pos AS POSS, r2.pts AS PTS', 'MATCH (t2:Team)-[r:BOXSCORE]->(GAME) WHERE TID <> t2.tid SET r.nrt = r.oef - OEF, r.pace = CASE WHEN r.mp <> 0 THEN $dr * ((r.pos + POSS) / (2 * r.mp)) ELSE 0 END, r.dp = r.pts - PTS, r.pc = PTS', {batchSize: $batchSize, params:{list_games: $list_games, dr: $dr}})"
	
	result = gu.execute_query(logger, ctx, championship, result_type, query, batchSize=BATCH_SIZE, list_games=list_games, dr=int(item["rt"]))
	
	if result['failedOperations'] > 0:
		logger.warning("%s :: %s :: SET_BOXSCORE_NRT_PACE_DP_PC :: %s :: %s", os.path.basename(__file__), os.getpid(), championship, result['failedOperations'])
	
	logger.info("%s :: %s :: SET_ADVANCED_STATISTICS_BETWEEN_TEAMS :: %s", os.path.basename(__file__), os.getpid(), util.get_duration(start_time))


def set_advanced_statistics_player(logger, ctx, championship, list_games=None):
	"""
	Function to calculate players advanced statistics.
	"""
	start_time = time.time()
	result_type = "single"
	
	# Get max ast and max agr
	query = "MATCH (p:Player)-[r:PLAYS]->(g:Game) WITH g.gid AS gid, p.pid AS pid, r.ast AS ast, sum(r.blk + r.stl + r.pf) AS agr, sum(r.fc + r.orb) AS oagr WITH pid, avg(ast) AS astAvg, avg(agr) AS agrAvg, avg(oagr) AS oagrAvg WITH max(astAvg) AS astMax, max(agrAvg) AS agrMax, max(oagrAvg) AS oagrMax RETURN ceil(astMax - 0.1 * astMax), ceil(agrMax - 0.1 * agrMax), ceil(oagrMax - 0.1 * oagrMax)"
	
	ast, agr, oagr = gu.execute_query(logger, ctx, championship, result_type, query)
	
	# Calculate statistics on PLAYS relation
	check_gid = "WHERE g.gid IN $list_games " if list_games is not None else ""
	query = "CALL apoc.periodic.iterate('MATCH (:Player)-[r:PLAYS]->(g:Game) "+check_gid+"RETURN r', 'SET "+field_goal()+", "+free_throw()+", "+three_points()+", "+total_rebounds()+", "+true_shooting()+", "+effective_field_goal()+", "+free_throw_rate()+", "+game_score()+", "+two_points_stats()+", "+points_per_minute()+", "+collective()+", "+aggressiveness()+", "+offensive_aggressiveness()+", "+altruism()+", "+assist_to_turnover()+", "+turnover_ratio()+"', {batchSize: $batchSize, params: {astMax: $astMax, agrMax: $agrMax, oagrMax: $oagrMax, list_games: $list_games}})"

	result = gu.execute_query(logger, ctx, championship, result_type, query, batchSize=BATCH_SIZE, list_games=list_games, astMax=ast, agrMax=agr, oagrMax=oagr)
	if result['failedOperations'] > 0:
		logger.warning("%s :: %s :: SET_PLAYS_FGP_FTP_TPP_TOR_TSP_EFGP_FTR_GMSC_TWP_TWPA_PPM_JDE_COL_AGR_OAGR_ALT_ATT :: %s :: %s", os.path.basename(__file__), os.getpid(), championship, result['failedOperations'])

	# Calculate statistics on PLAYS relation
	query = "CALL apoc.periodic.iterate('MATCH (:Player)-[r:PLAYS]->(g:Game) "+check_gid+"RETURN r', 'SET "+two_points_percentage()+", "+adress()+"', {batchSize: $batchSize, params: {list_games: $list_games}})"

	result = gu.execute_query(logger, ctx, championship, result_type, query, batchSize=BATCH_SIZE, list_games=list_games)

	if result['failedOperations'] > 0:
		logger.warning("%s :: %s :: SET_PLAYS_TWPP_ADS :: %s :: %s", os.path.basename(__file__), os.getpid(), championship, result['failedOperations'])


	# Calculate player impact estimate (PIE) on PLAYS relation
	# (GM = somme des BOXSCORE des deux équipes)
	query = "CALL apoc.periodic.iterate('MATCH (g:Game)<-[r1:BOXSCORE]-(:Team) "+check_gid+"RETURN g AS GAME, sum(r1.pts) AS GMPTS, sum(r1.fg) AS GMFG, sum(r1.ft) AS GMFT, sum(r1.fga) AS GMFGA, sum(r1.fta) AS GMFTA, sum(r1.drb) AS GMDRB, sum(r1.orb) AS GMORB, sum(r1.ast) AS GMAST, sum(r1.stl) AS GMSTL, sum(r1.blk) AS GMBLK, sum(r1.pf) AS GMPF, sum(r1.tov) AS GMTOV', 'MATCH (p:Player)-[r2:PLAYS]->(GAME) SET r2.pie = 100 * (r2.pts + r2.fg + r2.ft - r2.fga - r2.fta + r2.drb + (0.5 * r2.orb) + r2.ast + r2.stl + (0.5 * r2.blk) - r2.pf - r2.tov) / (GMPTS + GMFG + GMFT - GMFGA - GMFTA + GMDRB + (0.5 * GMORB) + GMAST + GMSTL + (0.5 * GMBLK) - GMPF - GMTOV)', {batchSize: $batchSize, params: {list_games: $list_games}})"

	result = gu.execute_query(logger, ctx, championship, result_type, query, batchSize=BATCH_SIZE, list_games=list_games)
	
	if result['failedOperations'] > 0:
		logger.warning("%s :: %s :: SET_PLAYS_PIE :: %s :: %s", os.path.basename(__file__), os.getpid(), championship, result['failedOperations'])

	# (r2 = BOXSCORE de son équipe)
	query = "CALL apoc.periodic.iterate('MATCH (p:Player)-[r1:PLAYS]->(g:Game)<-[r2:BOXSCORE]-(t:Team {tid: r1.tid}) "+check_gid+"RETURN r1, r2', 'SET "+usage()+", "+win_player()+", "+impact_per_minute()+", "+delta_plus_minus()+"', {batchSize: $batchSize, params: {list_games: $list_games}})"

	result = gu.execute_query(logger, ctx, championship, result_type, query, batchSize=BATCH_SIZE, list_games=list_games)
	
	if result['failedOperations'] > 0:
		logger.warning("%s :: %s :: SET_PLAYS_USG_WIN_DPM_PIEPM :: %s :: %s", os.path.basename(__file__), os.getpid(), championship, result['failedOperations'])

	# (r3 = BOXSCORE de l'autre équipe)
	check_gid = "WHERE g.gid IN $list_games " if list_games is not None else ""
	query = "CALL apoc.periodic.iterate('MATCH (:Player)-[r1:PLAYS]->(g:Game) "+check_gid+"WITH r1, g MATCH (:Team {tid: r1.tid})-[r2:BOXSCORE]->(g)<-[r3:BOXSCORE]-(:Team) RETURN r1, r2, r3', 'SET "+offensive_rebound_player()+", "+defensive_rebound_player()+"', {batchSize: $batchSize, params: {list_games: $list_games}})"

	result = gu.execute_query(logger, ctx, championship, result_type, query, batchSize=BATCH_SIZE, list_games=list_games)
	
	if result['failedOperations'] > 0:
		logger.warning("%s :: %s :: SET_PLAYS_ORBP_DRBP :: %s :: %s", os.path.basename(__file__), os.getpid(), championship, result['failedOperations'])
	
	# Calculate statistics on PLAYS relation
	query = "CALL apoc.periodic.iterate('MATCH (:Player)-[r:PLAYS]->(g:Game) "+check_gid+"RETURN r', 'SET "+four_factors()+", "+coach_game()+"', {batchSize: $batchSize, params: {list_games: $list_games}})"

	result = gu.execute_query(logger, ctx, championship, result_type, query, batchSize=BATCH_SIZE, list_games=list_games)

	if result['failedOperations'] > 0:
		logger.warning("%s :: %s :: SET_PLAYS_FF :: %s :: %s", os.path.basename(__file__), os.getpid(), championship, result['failedOperations'])

	logger.info("%s :: %s :: SET_ADVANCED_STATISTICS_PLAYER :: %s", os.path.basename(__file__), os.getpid(), util.get_duration(start_time))


def set_advanced_statistics_between_team_player(logger, ctx, championship, list_games=None):
	"""
	Function to calculate advanced statistics between teams and players.
	"""
	start_time = time.time()
	result_type = "single"
	
	# Calculate offensive efficiency on PLAYS relation.
	check_gid = "WHERE g.gid IN $list_games " if list_games is not None else ""
	query = "CALL apoc.periodic.iterate('MATCH (p:Player)-[r1:PLAYS]->(g:Game {played: true})<-[r2:BOXSCORE]-(t:Team {tid: r1.tid}) "+check_gid+"RETURN r1, r2', 'SET "+offensive_efficiency_player()+"', {batchSize: $batchSize, params: {list_games: $list_games}})"

	result = gu.execute_query(logger, ctx, championship, result_type, query, batchSize=BATCH_SIZE, list_games=list_games)
	
	if result['failedOperations'] > 0:
		logger.warning("%s :: %s :: SET_PLAYS_OEF :: %s :: %s", os.path.basename(__file__), os.getpid(), championship, result['failedOperations'])
	
	# Calculate defensive efficiency and net rating on PLAYS relation.
	check_gid = "WHERE g.gid IN $list_games AND t.tid <> r1.tid " if list_games is not None else "WHERE t.tid <> r1.tid "
	query = "CALL apoc.periodic.iterate('MATCH (p:Player)-[r1:PLAYS]->(g:Game)<-[r2:BOXSCORE]-(t:Team) "+check_gid+"RETURN p AS PLAYER, g AS GAME, r2.orb AS ORB, r2.fg AS FG, r2.fga AS FGA, r2.tov AS TOV, r2.fta AS FTA, r2.ft AS FT, r2.mp AS MP, r2.pts AS PTS, r2.pf AS PF', 'MATCH (PLAYER)-[r1:PLAYS]->(GAME)<-[r2:BOXSCORE]-(t:Team) WHERE t.tid = r1.tid SET "+defensive_efficiency_player()+"', {batchSize: $batchSize, params: {list_games: $list_games}})"
	
	result = gu.execute_query(logger, ctx, championship, result_type, query, batchSize=BATCH_SIZE, list_games=list_games)
	
	if result['failedOperations'] > 0:
		logger.warning("%s :: %s :: SET_PLAYS_DEF :: %s :: %s", os.path.basename(__file__), os.getpid(), championship, result['failedOperations'])

	# Calculate statistics on PLAYS relation
	check_gid = "WHERE g.gid IN $list_games " if list_games is not None else ""
	query = "CALL apoc.periodic.iterate('MATCH (:Player)-[r:PLAYS]->(g:Game) "+check_gid+"RETURN r', 'SET "+net_rating()+"', {batchSize: $batchSize, params: {list_games: $list_games}})"

	result = gu.execute_query(logger, ctx, championship, result_type, query, batchSize=BATCH_SIZE, list_games=list_games)

	if result['failedOperations'] > 0:
		logger.warning("%s :: %s :: SET_PLAYS_NRT :: %s :: %s", os.path.basename(__file__), os.getpid(), championship, result['failedOperations'])

	logger.info("%s :: %s :: SET_ADVANCED_STATISTICS_BETWEEN_TEAM_PLAYER :: %s", os.path.basename(__file__), os.getpid(), util.get_duration(start_time))


def set_advanced_statistics_game(logger, ctx, championship, list_games=None):
	"""
	Function to calculate games advanced statistics..
	"""
	start_time = time.time()
	result_type = "single"
	
	# Calculate if the game is being or have been played.
	check_gid = "WHERE g.gid IN $list_games " if list_games is not None else ""
	query = "CALL apoc.periodic.iterate('MATCH (g:Game) "+check_gid+"WITH g OPTIONAL MATCH (:Team)-[b:BOXSCORE]->(g)<-[p:PLAYS]-(:Player) RETURN g, CASE WHEN count(p) > 0 AND all(val IN collect(b.pts) WHERE val > 0) THEN true ELSE false END AS played', 'SET g.played = played', {batchSize: $batchSize, params: {list_games: $list_games}})"

	result = gu.execute_query(logger, ctx, championship, result_type, query, batchSize=BATCH_SIZE, list_games=list_games)
	
	if result['failedOperations'] > 0:
		logger.warning("%s :: %s :: SET_GAME_PLAYED :: %s :: %s", os.path.basename(__file__), os.getpid(), championship, result['failedOperations'])
	
	logger.info("%s :: %s :: SET_ADVANCED_STATISTICS_GAME :: %s", os.path.basename(__file__), os.getpid(), util.get_duration(start_time))


def set_statistics(logger, ctx, championship, list_games):
	"""
	Function to set statistics on PLAYS and BOXSCORE relations.
	"""
	set_pbp_teams_statistics(logger, ctx, championship, list_games)
	set_pbp_players_statistics(logger, ctx, championship, list_games)
	set_advanced_statistics_game(logger, ctx, championship, list_games)
	set_advanced_statistics_team(logger, ctx, championship, list_games)
	set_advanced_statistics_between_teams(logger, ctx, championship, list_games)
	set_advanced_statistics_player(logger, ctx, championship, list_games)
	set_advanced_statistics_between_team_player(logger, ctx, championship, list_games)


def set_pbp_teams_statistics(logger, ctx, championship, list_games):
	"""
	Function to set play-by-play teams statistics (time_tied, time_lead_home, time_lead_away, lead_changes, ties, spread, time_drought_home and time_drought_visitor).
	"""
	start_time = time.time()

	check_gid = " AND game.gid IN $list_games" if list_games is not None else ""
	query = """
		CALL apoc.periodic.iterate(
			' 
				MATCH (homeTeam)-[r1:BOXSCORE]->(game:Game 
					WHERE game.gid =~ "(?i)[0-9]{9}"+homeTeam.shn
					"""+check_gid+"""
				)<-[r2:BOXSCORE]-(visitorTeam) 
				RETURN homeTeam, r1, game, r2, visitorTeam
			', '
				CALL (game, r1) {
					WITH 
						r1, 
						apoc.coll.sortNodes([(event)-[:OCCURS_IN]->(game) | event], "^sec") AS events, 
						apoc.coll.sortNodes([(event)-[:OCCURS_IN]->(game) WHERE event.hscr <> event.vscr | event], "^sec") AS events_scr_diff 
					UNWIND range(0, size(events)-1) AS i 
					WITH 
						events[i] AS event, 
						reduce(acc = 0, j IN range(0, i) | (coalesce(events[j+1].sec, r1.mp*60) - events[j].sec)) AS diff, 
						events_scr_diff, 
						events 
					WITH 
						collect({event: event, diff: diff}) AS results, 
						events_scr_diff, 
						[event IN events | event.hscr = event.vscr] AS events, 
						apoc.coll.max([event IN events WHERE event.hscr > event.vscr | event.sprd]) AS spread_home, 
						apoc.coll.max([event IN events WHERE event.hscr < event.vscr | event.sprd]) AS spread_away 
					CALL (results) {
						UNWIND results AS result 
						RETURN result.event.hscr AS scr, sum(result.diff) AS time_drought 
						ORDER BY time_drought DESC LIMIT 1 
						UNION ALL 
						UNWIND results AS result 
						RETURN result.event.vscr AS scr, sum(result.diff) AS time_drought 
						ORDER BY time_drought DESC LIMIT 1
					} 
					WITH 
						collect(time_drought) AS time_droughts, 
						events, 
						coalesce(apoc.coll.sum([result IN results WHERE result.event.hscr = result.event.vscr | result.diff]), 0) AS time_tied, 
						coalesce(apoc.coll.sum([result IN results WHERE result.event.hscr > result.event.vscr | result.diff]), 0) AS time_lead_home, 
						coalesce(apoc.coll.sum([result IN results WHERE result.event.hscr < result.event.vscr | result.diff]), 0) AS time_lead_away, 
						size(apoc.coll.dropDuplicateNeighbors([event IN events_scr_diff | CASE WHEN event.hscr > event.vscr THEN "Home" ELSE "Away" END])) - 1 AS lead_changes, 
						spread_home, 
						spread_away 
					CALL apoc.coll.split(events, False) 
					YIELD value 
					RETURN 
						size(collect(value)) AS ties, 
						time_droughts[0] AS time_drought_home, 
						time_droughts[1] AS time_drought_away, 
						time_tied, time_lead_home, time_lead_away, lead_changes, 
						spread_home, spread_away		
				} 
				WITH homeTeam, r1, game, r2, visitorTeam, time_tied, time_lead_home, time_lead_away, lead_changes, ties, spread_home, spread_away, time_drought_home, time_drought_away 
				SET r1 += {
					eq: ties, 
					lt: time_lead_home, 
					lc: lead_changes, 
					sprd: spread_home, 
					td: time_drought_home
				}, 
				r2 += {
					eq: ties, 
					lt: time_lead_away, 
					lc: lead_changes, 
					sprd: spread_away, 
					td: time_drought_away
				}
			', {batchSize: $batchSize, params: {list_games: $list_games}})
		"""

	result = gu.execute_query(logger, ctx, championship, "single", query, batchSize=BATCH_SIZE, list_games=list_games)
	
	if result['failedOperations'] > 0:
		logger.warning("%s :: %s :: SET_BOXSCORE_EQ_LT_LC_SPRD_TD :: %s :: %s", os.path.basename(__file__), os.getpid(), championship, result['failedOperations'])
	
	logger.info("%s :: %s :: SET_PBP_TEAMS_STATISTICS :: %s", os.path.basename(__file__), os.getpid(), util.get_duration(start_time))


def set_pbp_players_statistics(logger, ctx, championship, list_games):
	"""
	Function to set play-by-play players statistics (cluch_moment, passes_received and fouls_caused).
	"""
	start_time = time.time()

	check_gid = " WHERE game.gid IN $list_games" if list_games is not None else ""

	query = """
		CALL apoc.periodic.iterate(
			' 
				MATCH (game:Game"""+check_gid+""") 
				RETURN game
			', '
				WITH game 
				MATCH (game)<-[rp:PLAYS]-(player) 
				OPTIONAL MATCH (game)<-[:OCCURS_IN]-(event WHERE event.quarter >= 4 AND event.sprd <= 15) 
				WHERE EXISTS { (event)<-[:BLOCK|TWO_PT_MISSED|OFF_REBOUND|TURNOVER|TWO_PT_MADE|THREE_PT_MADE|ASSIST|THREE_PT_MISSED|DEF_REBOUND|SHOOTING_FOUL|FT_MADE|PERSONAL_FOUL|STEAL|OFFENSIVE_FOUL|FT_MISSED|DEFENSIVE_FOUL|TECHNICAL_FOUL]-(player) } 
				WITH 
					player, 
					rp, 
					event, 
					toFloat(CASE WHEN event.quarter <= 4 THEN abs(48 - ((event.sec / 60) + 12)) ELSE abs(48 - ((event.sec / 60) + 5)) END) / (event.sprd + 1) AS coef 
				ORDER BY event.sec 
				WITH 
					player, 
					rp, 
					apoc.coll.sum([(player)-[r:BLOCK|TWO_PT_MISSED|OFF_REBOUND|TURNOVER|TWO_PT_MADE|THREE_PT_MADE|ASSIST|THREE_PT_MISSED|DEF_REBOUND|SHOOTING_FOUL|FT_MADE|PERSONAL_FOUL|STEAL|OFFENSIVE_FOUL|FT_MISSED|DEFENSIVE_FOUL|TECHNICAL_FOUL]->(event) | CASE 
						WHEN type(r) = "TWO_PT_MISSED" THEN -1 * coef 
						WHEN type(r) = "TWO_PT_MADE" THEN 2 * coef 
						WHEN type(r) = "THREE_PT_MISSED" THEN -1.5 * coef 
						WHEN type(r) = "THREE_PT_MADE" THEN 3 * coef 
						WHEN type(r) = "FT_MISSED" THEN -1 * coef 
						WHEN type(r) = "FT_MADE" THEN 1 * coef 
						WHEN type(r) = "ASSIST" THEN 1 * coef 
						WHEN type(r) = "BLOCK" THEN 1.5 * coef 
						WHEN type(r) = "DEF_REBOUND" THEN 0.5 * coef 
						WHEN type(r) = "OFF_REBOUND" THEN 1 * coef 
						WHEN type(r) = "TURNOVER" THEN -1.5 * coef 
						WHEN type(r) = "SHOOTING_FOUL" THEN -0.5 * coef 
						WHEN type(r) = "PERSONAL_FOUL" THEN -0.5 * coef 
						WHEN type(r) = "TECHNICAL_FOUL" THEN -2 * coef
						WHEN type(r) = "OFFENSIVE_FOUL" THEN -0.5 * coef 
						WHEN type(r) = "STEAL" THEN 1.5 * coef 
						WHEN type(r) = "DEFENSIVE_FOUL" THEN -0.5 * coef 
					END]) AS value 
				WITH rp, 50 + sum(value) AS cm 
				SET rp.cm = cm	
			', {batchSize: $batchSize, params: {list_games: $list_games}})
		"""
	result = gu.execute_query(logger, ctx, championship, "single", query, batchSize=BATCH_SIZE, list_games=list_games)
	
	if result['failedOperations'] > 0:
		logger.warning("%s :: %s :: SET_PLAYS_CM :: %s :: %s", os.path.basename(__file__), os.getpid(), championship, result['failedOperations'])

	query = """
		CALL apoc.periodic.iterate(
			' 
				MATCH (game:Game"""+check_gid+""") 
				RETURN game
			', '
				CALL (game) {
					MATCH (player)-[r1:PLAYS]->(game) 
					CALL (player, r1, game) {
						MATCH (game)<-[:OCCURS_IN]-(event) 
						WHERE EXISTS {
							MATCH (event)<-[:TWO_PT_MADE|THREE_PT_MADE]-(player) 
							MATCH (event)<-[:ASSIST]-(other_player)-[:PLAYS {tid: r1.tid}]->(game)
						} 
						RETURN count(*) AS nb
						UNION ALL 
						MATCH (game)<-[:OCCURS_IN]-(event) 
						WHERE EXISTS {
							MATCH (event)<-[:FT_MADE|FT_MISSED]-(player) 
							MATCH (event)<-[:SHOOTING_FOUL|PERSONAL_FOUL|TECHNICAL_FOUL|OFFENSIVE_FOUL|DEFENSIVE_FOUL]-(other_player)-[r2:PLAYS]->(game) 
							WHERE r1.tid <> r2.tid
						} 
						RETURN count(*) AS nb
					} 
					RETURN player, collect(nb) AS stats, r1
				} 
				WITH player, r1, stats[0] AS passes_received, stats[1] AS fouls_caused 
				SET r1 += {
					pr: passes_received, 
					fc: fouls_caused
				}
			', {batchSize: $batchSize, params: {list_games: $list_games}})
		"""

	result = gu.execute_query(logger, ctx, championship, "single", query, batchSize=BATCH_SIZE, list_games=list_games)
	
	if result['failedOperations'] > 0:
		logger.warning("%s :: %s :: SET_PLAYS_PR_FC :: %s :: %s", os.path.basename(__file__), os.getpid(), championship, result['failedOperations'])
	
	logger.info("%s :: %s :: SET_PBP_PLAYERS_STATISTICS :: %s", os.path.basename(__file__), os.getpid(), util.get_duration(start_time))
