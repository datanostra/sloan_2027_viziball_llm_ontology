#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
import re
import pandas as pd
import numpy as np
from datetime import datetime
from itertools import groupby
from operator import itemgetter
import app.pbp as pbp
import app.graph.util as gu
import app.graph.calculate as gc


def get_mvp():
	"""
	Function to get all MVPs of the day.
	parameters: date
	"""
	return """
		MATCH (home_team)-[:BOXSCORE]->(game:Game 
			WHERE game.dat = $date 
			AND game.played = true 
			AND game.gid =~ '(?i)[0-9]{9}'+home_team.shn
		)<-[:BOXSCORE]-(visitor_team) 
		WITH game, home_team, visitor_team 
		CALL (game) { 
			MATCH (game)<-[r:PLAYS {win: 1}]-(player) 
			RETURN player.ln AS lastname, player.fn AS firstname, round(max(r.pie), 2) AS max 
			ORDER BY max DESC LIMIT 1 
		} 
		RETURN 
			apoc.text.join([firstname, lastname], ' ') AS nom, 
			max AS pie, 
			CASE WHEN substring(game.gid, 9) = home_team.shn THEN home_team.nik + ' vs ' + visitor_team.nik ELSE visitor_team.nik + ' vs ' + home_team.nik END AS match 
			ORDER BY pie DESC
		"""


def get_simple_report(logger, ctx, championship, date):
	"""
	Function to get the main information (date, seasons, calendar, mvp & last_match_date) for a date (YYYYMMDD).
	"""
	query_seasons = """
		MATCH (season:Season) 
		WITH apoc.map.removeKeys(properties(season), ['sid']) AS data 
		ORDER BY season.start DESC 
		RETURN collect(data)
		"""
	seasons = gu.execute_query(logger, ctx, championship, "single", query_seasons)[0]
	query_dates = """
		MATCH (game:Game WHERE game.played = true) 
		WITH game.dat AS last 
		ORDER BY last DESC LIMIT 1 
		WITH last, coalesce($date, last) AS current_date 
		CALL (current_date) { 
			MATCH (game:Game WHERE game.dat < current_date) 
			RETURN {previous: game.dat} AS date 
			ORDER BY game.dat DESC LIMIT 1 
			UNION 
			MATCH (game:Game WHERE game.dat > current_date) 
			RETURN {next: game.dat} AS date 
			ORDER BY game.dat LIMIT 1 
		} 
		WITH 
			{last: last, system_date: toString(datetime())} AS part_1, 
			apoc.map.mergeList(collect(date)) AS part_2 
		RETURN 
			apoc.map.merge(part_1, part_2)
		"""
	dates = gu.execute_query(logger, ctx, championship, "single", query_dates, date=date)[0]
	date = dates['last'] if date is None else date
	query_report = """
		MATCH (home_team)-[b1:BOXSCORE]->(game:Game 
			WHERE game.dat = $date 
			AND game.gid =~ '(?i)[0-9]{9}'+home_team.shn
		)<-[b2:BOXSCORE]-(visitor_team)
		RETURN 
			game.hr AS hr, 
			home_team.nik AS hTeam, 
			home_team.hcl AS hHcl, 
			home_team.vcl AS hVcl, 
			CASE WHEN game.played = true THEN b1.pts ELSE 0 END AS hPts, 
			home_team.shn AS hShn, 
			visitor_team.nik AS vTeam, 
			visitor_team.hcl AS vHcl, 
			visitor_team.vcl AS vVcl, 
			CASE WHEN game.played = true THEN b2.pts ELSE 0 END AS vPts, 
			visitor_team.shn AS vShn
		"""
	report = gu.execute_query(logger, ctx, championship, "list", query_report, date=date)
	mvp = gu.execute_query(logger, ctx, championship, "list", get_mvp(), date=date)
	return {"date": date, "seasons": seasons, "calendar": report, "mvp": (mvp[0] if len(mvp) > 0 else {}), **dates}


def get_full_report(logger, ctx, championship, date, nick):
	"""
	Function to get the full report for a match thanks to the date and the nickname of the team.
	"""
	query = """
		MATCH (team:Team WHERE team.nik =~ '(?i)'+$nick) 
		MATCH (game:Game WHERE game.dat = $date AND game.gid =~ '(?i)[0-9]{9}'+team.shn) 
		RETURN 
			apoc.map.removeKeys(apoc.map.mergeList([properties(game), apoc.map.mergeList([(t)-[b:BOXSCORE]->(game) | CASE WHEN substring(game.gid, 9) = t.shn THEN {hTeam: t.shn, hPts: b.pts, hTid: t.tid} ELSE {vTeam: t.shn, vPts: b.pts, vTid: t.tid} END])]), ['gid', 'description']) AS game, 
			[(t)-[b:BOXSCORE]->(game) | apoc.map.removeKeys(apoc.map.mergeList([properties(t), properties(b)]), ['div', 'fra', 'cty', 'cnf'])] AS teams, 
			[(player)-[r:PLAYS]->(game) | apoc.map.mergeList([properties(player), properties(r)])] AS players, 
			toString(datetime()) AS system_date
		"""
	data = gu.execute_query(logger, ctx, championship, "list", query, nick=nick, date=int(date))
	return data[0] if len(data) > 0 else {}


def get_last_full_report(logger, ctx, championship):
	"""
	Function to get the full report of the last match.
	"""
	query = """
		MATCH (game:Game 
			WHERE game.played = true
		)<-[:BOXSCORE]-(team) 
		WHERE game.gid =~ '(?i)[0-9]{9}'+team.shn 
		RETURN game.dat, team.nik 
		ORDER BY game.dat DESC LIMIT 1
		"""
	data = gu.execute_query(logger, ctx, championship, "single", query)
	return get_full_report(logger, ctx, championship, data[0], data[1]) if data is not None and len(data) > 0 else {}


def get_teams_last_full_report(logger, ctx, championship, team1, team2):
	"""
	Function to get the full report of the last match of the season between two teams.
	"""
	query = """
		MATCH (home_team:Team 
			WHERE home_team.nik =~ '(?i)'+$team1
		)-[:BOXSCORE]->(game:Game 
			WHERE game.played = true 
			AND game.gid =~ '(?i)[0-9]{9}'+home_team.shn
		)<-[:BOXSCORE]-(visitor_team:Team 
			WHERE visitor_team.nik =~ '(?i)'+$team2) 
		RETURN game.dat, home_team.nik 
		ORDER BY game.dat DESC LIMIT 1
		"""
	data = gu.execute_query(logger, ctx, championship, "single", query, team1=team1, team2=team2)
	return get_full_report(logger, ctx, championship, data[0], data[1]) if data is not None and len(data) > 0 else {}


def get_preview_report(logger, ctx, championship, date, nick):
	"""
	Function to get the preview report for a match thanks to the date and the nickname of the team.
	"""
	query = """
		MATCH (team:Team WHERE team.nik =~ '(?i)'+$nick) 
		MATCH (t)-[b:BOXSCORE]->(game:Game WHERE game.dat = $date AND game.gid =~ '(?i)[0-9]{9}'+team.shn) 
		RETURN 
			collect(apoc.map.removeKeys(apoc.map.mergeList([properties(t), {dist: b.dist, rd: b.rd}]), ['div', 'fra', 'cty', 'cnf', 'lat', 'long'])) AS teams, 
			game.played AS played"""
	data = gu.execute_query(logger, ctx, championship, "list", query, nick=nick, date=int(date))
	return data[0] if len(data) > 0 else []


def get_player_ranking(logger, ctx, championship, date_start, date_end, stat, nb_matches=100, limit=10, operator="avg", sort="DESC", mp_min=0, mp_max=100, p_min=0, p_max=100, teams="all", nationalities="all"):
	"""
	Function to get the ranking of players for a choosen statistic.
	"""
	stat = str(stat).lower()
	operator = "avg" if str(operator).lower() not in ["avg", "min", "max", "sum", "stdev", "median", "variance"] else operator
	sort = "" if str(sort).upper() == "ASC" else "DESC"
	mp_max = 100 if mp_max > 48 else mp_max
	mp_min = 0 if mp_min < 0 else mp_min
	p_max = 100 if p_max > 100 else p_max
	p_min = 0 if p_min < 0 else p_min
	nb_matches = 1 if nb_matches < 0 else nb_matches
	limit = 10 if limit > 100 or limit < 1 else limit
	ope_tmp = "percentileDisc(stat, 0.5)" if operator == "median" else "percentileDisc(stat, 0.5)^2" if operator == "variance" else operator+"(stat)"
	# Filter teams
	if teams.lower() != "all":
		filter_team = "WHERE r.tid IN $teams "
		teams = list(map(int, teams.split("-")))
	else:
		filter_team = ""
		teams = []
	# Filter nationalities
	if nationalities.lower() != "all":
		filter_nationalities = " WHERE player.nat IN $nationalities"
		nationalities = nationalities.split("-")
	else:
		filter_nationalities = ""
		nationalities = []
	# Filter statistics with avg
	statistics = gc.get_percentage_statistics_formula()
	if operator == "avg" and stat in list(statistics.keys()):
		query = """
			MATCH (player"""+filter_nationalities+""")-[r:PLAYS]->(game:Game WHERE game.played = true AND $date_start <= game.dat <= $date_end) 
			"""+filter_team+""" 
			WITH player.pid AS pid, player.fn AS fn, player.ln AS ln, """+statistics[stat]["row"]+""", r.win AS win, {gid: game.gid, team: r.tid} AS matches, r.mp AS mp 
			ORDER BY game.dat DESC 
			WITH pid, fn, ln, """+statistics[stat]["formula"]+""" AS stat, round(toFloat(sum(win)) / toFloat(count(win)), 2) * 100 AS winPercentage, collect(matches) AS matches, round(avg(mp), 2) AS mp, count(matches) >= $nb_matches AS check 
			WHERE check = True 
			AND $mp_min <= mp <= $mp_max 
			AND $p_min <= winPercentage <= $p_max 
			WITH * 
			ORDER BY stat """+sort+""", winPercentage """+sort+""" 
			LIMIT $limit 
			CALL (matches) { 
				MATCH (team:Team {tid: matches[0]['team']}) 
				RETURN team.hcl AS hcl, team.vcl AS vcl, team.shn AS shn, team.tid AS tid
			} 
			RETURN pid, fn, ln, mp AS mp2, round(stat, 2) AS """+stat+""", hcl, vcl, shn, tid, size(matches) AS x, winPercentage
			"""
	else:
		query = """
			MATCH (player"""+filter_nationalities+""")-[r:PLAYS]->(game:Game WHERE game.played = true AND $date_start <= game.dat <= $date_end) 
			"""+filter_team+""" 
			WITH player.pid AS pid, player.fn AS fn, player.ln AS ln, r[$stat] AS stat, r.win AS win, {gid: game.gid, team: r.tid} AS matches, r.mp AS mp 
			ORDER BY game.dat DESC 
			WITH pid, fn, ln, """+ope_tmp+""" AS stat, round(toFloat(sum(win)) / toFloat(count(win)), 2) * 100 AS winPercentage, collect(matches) AS matches, round(avg(mp), 2) AS mp, count(matches) >= $nb_matches AS check 
			WHERE check = True 
			AND $mp_min <= mp <= $mp_max 
			AND $p_min <= winPercentage <= $p_max 
			WITH * 
			ORDER BY stat """+sort+""", winPercentage """+sort+""" 
			LIMIT $limit 
			CALL (matches) { 
				MATCH (team:Team {tid: matches[0]['team']}) 
				RETURN team.hcl AS hcl, team.vcl AS vcl, team.shn AS shn, team.tid AS tid
			} 
			RETURN pid, fn, ln, mp AS mp2, round(stat, 2) AS """+stat+""", hcl, vcl, shn, tid, size(matches) AS x, winPercentage
			"""
	return gu.execute_query(logger, ctx, championship, "list", query, date_start=int(date_start), date_end=int(date_end), stat=stat, limit=limit, nb_matches=nb_matches, mp_min=mp_min, mp_max=mp_max, p_min=p_min, p_max=p_max, teams=teams, nationalities=nationalities)


def get_team_ranking(logger, ctx, championship, date_start, date_end, stat, nb_matches=100, limit=10, operator="avg", sort="DESC", p_min=0, p_max=100):
	"""
	Function to get the ranking of teams for a choosen statistic.
	"""
	stat = str(stat).lower()
	operator = "avg" if str(operator).lower() not in ["avg", "min", "max", "sum", "stdev", "median", "variance"] else operator
	sort = "" if str(sort).upper() == "ASC" else "DESC"
	p_max = 100 if p_max > 100 else p_max
	p_min = 0 if p_min < 0 else p_min
	nb_matches = 1 if nb_matches < 0 else nb_matches
	limit = 10 if limit > 100 or limit < 1 else limit
	ope_tmp = "percentileDisc(r[$stat], 0.5)" if operator == "median" else "percentileDisc(r[$stat], 0.5)^2" if operator == "variance" else operator+"(r[$stat])"
	query = """
		MATCH (team)-[r:BOXSCORE]->(game:Game WHERE game.played = true AND $date_start <= game.dat <= $date_end) 
		WITH team.tid AS tid, team.shn AS shn, team.nik AS nik, team.cty AS cty, team.hcl AS hcl, team.vcl AS vcl, round("""+ope_tmp+""", 2) AS """+stat+""", toFloat(sum(r.win)) AS win, toFloat(count(r.win)) AS matches, count(r) AS x, round(toFloat(sum(r.win)) / toFloat(count(r.win)), 2) * 100 AS winPercentage 
		WHERE matches >= $nb_matches 
		AND $p_min <= winPercentage <= $p_max 
		RETURN tid, shn, nik, cty, hcl, vcl, """+stat+""", x, round(win / matches, 2) * 100 AS winPercentage ORDER BY """+stat+""" """+sort+""", winPercentage """+sort+""" 
		LIMIT $limit
		"""
	return gu.execute_query(logger, ctx, championship, "list", query, date_start=int(date_start), date_end=int(date_end), stat=stat, limit=limit, nb_matches=nb_matches, p_min=p_min, p_max=p_max)


def get_game_result_between_teams(logger, ctx, championship, date, team1, team2, nb_matchs):
	"""
	Function to get the result of last matches between two teams.
	"""
	query = """
		MATCH (home_team:Team)-[r1:BOXSCORE]->(game:Game 
			WHERE game.dat < $date 
			AND game.played = true 
			AND game.gid =~ '(?i)[0-9]{9}'+home_team.shn
		)<-[r2:BOXSCORE]-(visitor_team:Team) 
		WHERE (
			(home_team.nik =~ $team1 AND visitor_team.nik =~ $team2) 
			OR 
			(home_team.nik =~ $team2 AND visitor_team.nik =~ $team1))
		WITH {gid: game.gid, hScore: r1.pts, hTeam: home_team.tid, vScore: r2.pts, vTeam: visitor_team.tid} AS history 
		ORDER BY history.gid DESC LIMIT $nb_matchs 
		WITH collect(history) AS history 
		MATCH (team:Team WHERE team.nik =~ $team1 OR team.nik =~ $team2) 
		RETURN history, collect(apoc.map.removeKeys(properties(team), ['div', 'fra', 'cty', 'cnf'])) AS teams
		"""
	data = gu.execute_query(logger, ctx, championship, "list", query, team1='(?i)'+team1, team2='(?i)'+team2, date=int(date), nb_matchs=int(nb_matchs))
	return data[0] if len(data) > 0 else {}


def linear_regression(stat):
	"""
	Function for calculating the linear regression coefficients for a statistic.
	"""
	p = np.polyfit(np.arange(0, len(stat)), np.array(stat), 1)
	return round(p[0], 2), round(p[1], 2)


def get_stat_result_by_teams(logger, ctx, championship, date, team1, team2, stat, nb_matchs):
	"""
	Function to get values of a choosen statistic for two teams during their last own matches.
	"""
	stat = str(stat).lower()
	query = """
		MATCH (season:Season WHERE season.start <= $date) 
		WITH season.start AS start 
		ORDER BY start DESC LIMIT 1 
		MATCH (home_team:Team 
			WHERE home_team.nik =~ '(?i)'+$team1 OR home_team.nik =~ '(?i)'+$team2
		)-[r1:BOXSCORE]->(game:Game 
			WHERE start <= game.dat < $date 
			AND game.played = true
		)<-[r2:BOXSCORE]-(visitor_team) 
		WITH home_team.tid AS tid, home_team.shn AS shn, home_team.nik AS nik, home_team.vcl AS vcl, home_team.hcl AS hcl, r1[$stat] AS x, game.dat AS date, visitor_team.nik AS t2Nik, visitor_team.shn AS t2Shn, r2.pts AS r2Pts, r1.win AS win, CASE WHEN game.gid =~ '(?i)[0-9]{9}'+home_team.shn THEN 1 ELSE 0 END AS home, game.gid AS gid 
		ORDER BY date DESC 
		WITH tid, nik, shn, hcl, vcl, size(collect(gid)) AS nb_matchs, reverse(collect(round(x, 2))[0..$nb_matchs]) AS x, reverse(collect(win)[0..$nb_matchs]) AS win, reverse(collect(home)[0..$nb_matchs]) AS home, reverse(collect({date: date, nik: t2Nik, shn: t2Shn, x: r2Pts})[0..$nb_matchs]) AS games 
		RETURN tid, nik, shn, hcl, vcl, nb_matchs, x, win, home, games
		"""
	df = gu.execute_query(logger, ctx, championship, "df", query, team1=team1, team2=team2, date=int(date), stat=stat, nb_matchs=int(nb_matchs))
	result = {}
	if len(df.index) > 0:
		df.fillna(value=0, inplace=True)
		df['a'], df['b'] = zip(*[linear_regression(x) if len(x) > 1 else (0, 0) for x in df['x']])
		df['mean'] = [round(np.mean(x), 2) for x in df['x']]
		df['std'] = [round(np.std(x), 2) for x in df['x']]
		result = {"teams": df[["tid", "shn", "nik", "hcl", "vcl"]].to_dict(orient='records'), "stat": stat, "values": df[["tid", "nb_matchs", "x", "win", "home", "a", "b", "mean", "std", "games"]].to_dict(orient='records')}
	return result


def get_stat_result_by_players(logger, ctx, championship, date, team1, team2, stat, nb_matchs):
	"""
	Function to get the trend of a choosen statistic for players of two teams.
	"""
	stat = str(stat).lower()
	query = """
		MATCH (season:Season WHERE season.start <= $date) 
		WITH season.start AS start 
		ORDER BY start DESC LIMIT 1 
		MATCH (team:Team 
			 WHERE team.nik =~ '(?i)'+$team1 OR team.nik =~ '(?i)'+$team2
		)-[:BOXSCORE]->(game:Game WHERE start <= game.dat < $date AND game.played = true) 
		WITH game.gid AS gid, team.tid AS tid, team.shn AS shn, team.nik AS nik, team.hcl AS hcl, team.vcl AS vcl 
		ORDER BY gid DESC 
		WITH $stat AS s, collect(gid)[0..$nb_matchs] AS gids, tid AS tid, shn AS shn, nik AS nik, hcl AS hcl, vcl AS vcl 
		CALL (s, tid, gids) { 
			MATCH (player)-[r:PLAYS {tid: tid}]->(game:Game WHERE game.gid IN gids) 
			WITH player.pid AS pid, player.fn AS fn, player.ln AS ln, r[s] AS stat, r.mp AS mp, game.dat AS dat 
			ORDER BY game.dat 
			RETURN pid, fn, ln, collect(stat) AS stat, collect(mp) AS mp, collect(dat)[-1] AS lastMatch 
		} 
		WITH pid, fn, ln, tid, stat, mp, lastMatch, shn, nik, hcl, vcl 
		ORDER BY lastMatch DESC 
		RETURN pid, fn, ln, collect(tid)[0] AS tid, collect(stat)[0] AS stat, collect(mp)[0] AS mp, collect(shn)[0] AS shn, collect(nik)[0] AS nik, collect(hcl)[0] AS hcl, collect(vcl)[0] AS vcl 
		ORDER BY tid
		"""
	df = gu.execute_query(logger, ctx, championship, "df", query, team1=team1, team2=team2, date=int(date), stat=stat, nb_matchs=int(nb_matchs))
	result = {}
	if len(df.index) > 0:
		df.fillna(value=0, inplace=True)
		df['nbGames'] = [len(x) for x in df['stat']]
		df['mpMean'] = [round(np.mean(x), 2) for x in df['mp']]
		df['trend'] = [linear_regression(x)[0] if len(x) > 1 else 0 for x in df['stat']]
		df['mean'] = [round(np.mean(x), 2) for x in df['stat']]
		df['std'] = [round(np.std(x), 2) for x in df['stat']]
		df['sum'] = [round(np.sum(x), 2) for x in df['stat']]
		df['max'] = [round(np.max(x), 2) for x in df['stat']]
		df['min'] = [round(np.min(x), 2) for x in df['stat']]
		df['variance'] = [round(np.var(x), 2) for x in df['stat']]
		df['median'] = [round(np.median(x), 2) for x in df['stat']]
		result = {"teams": df[["tid", "shn", "nik", "hcl", "vcl"]].drop_duplicates().to_dict(orient='records'), "stat": stat, "values": df[df.columns.difference(["shn", "nik", "hcl", "vcl", "stat", "mp"])].to_dict(orient='records')}
	return result


def get_stat_result_avg_by_players(logger, ctx, championship, date, team1, team2, nb_matchs):
	"""
	Function to get the average of several statistics for players of two teams.
	"""
	query = """
		MATCH (season:Season WHERE season.start <= $date) 
		WITH season.start AS start 
		ORDER BY start DESC LIMIT 1 
		MATCH (team:Team 
			 WHERE team.nik =~ '(?i)'+$team1 OR team.nik =~ '(?i)'+$team2
		)-[:BOXSCORE]->(game:Game WHERE start <= game.dat < $date AND game.played = true) 
		WITH team.tid AS tid, game.gid AS gid 
		ORDER BY gid DESC 
		WITH tid, collect(gid)[0..$nb_matchs] AS gids 
		CALL (tid, gids) { 
			MATCH (player)-[r:PLAYS {tid: tid}]->(game:Game WHERE game.gid IN gids) 
			WITH player.fn AS fn, player.ln AS ln, r.ast AS ast, r.blk AS blk, r.fg AS fg, r.fga AS fga, r.pf AS pf, r.stl AS stl, r.tov AS tov, r.tp AS tp, r.tpa AS tpa, r.twp AS twp, r.twpa AS twpa, r.fta AS fta 
			RETURN fn, ln, round(avg(ast), 2)  AS ast, round(avg(blk), 2) AS blk, round(avg(fg), 2) AS fg, round(avg(fga), 2) AS fga, round(avg(pf), 2) AS pf, round(avg(stl), 2) AS stl, round(avg(tov), 2) AS tov, round(avg(tp), 2) AS tp, round(avg(tpa), 2) AS tpa, round(avg(twp), 2) AS twp, round(avg(twpa), 2) AS twpa, round(avg(fta), 2) AS fta 
		} 
		RETURN fn AS fn, ln AS ln, tid, ast AS ast, blk AS blk, fg AS fg, fga AS fga, pf AS pf, stl AS stl, tov AS tov, tp AS tp, tpa AS tpa, twp AS twp, twpa AS twpa, fta AS fta
		"""
	return gu.execute_query(logger, ctx, championship, "list", query, team1=team1, team2=team2, date=int(date), nb_matchs=int(nb_matchs))


def get_database_information(logger, ctx, championship):
	"""
	Function to get all information of the database.
	"""
	query = """
		CALL () { 
			MATCH (game:Game WHERE game.played = true) 
			RETURN 'Game' AS label, count(game) AS total 
			UNION ALL 
			MATCH (player:Player WHERE EXISTS((player)-[:PLAYS]->(:Game))) 
			RETURN 'Player' AS label, count(player) AS total 
			UNION ALL 
			MATCH (season:Season) 
			RETURN 'Season' AS label, count(season) AS total 
		} 
		RETURN label, total
		"""
	return gu.execute_query(logger, ctx, championship, "list", query)


def get_happy_birthday(logger, ctx, championship, stat="gmsc", date=None):
	"""
	Function to get the best game of the players according to their date of birth.
	"""
	date = str(datetime.today().strftime('%m%d')) if date is None else str(datetime.strptime(str(date), '%Y%m%d').strftime('%m%d'))
	query = """
		MATCH (player:Player WHERE toString(player.bth) =~ '[0-9]{4}'+$date) 
		WITH player 
		CALL (player) { 
			MATCH (player)-[r:PLAYS]->(game) 
			RETURN game, round(max(r[$stat]), 2) AS stat 
			ORDER BY stat DESC LIMIT 1 
		} 
		WITH player, game, stat 
		CALL (game) { 
			MATCH (home_team)-[:BOXSCORE]->(game 
				WHERE game.gid =~ '(?i)[0-9]{9}'+home_team.shn
			)<-[:BOXSCORE]-(visitor_team) 
			RETURN game.dat AS date, home_team.nik AS team1, visitor_team.nik AS team2 
			LIMIT 1 
		} 
		RETURN 
			player.pid AS pid, 
			apoc.text.join([player.fn, player.ln], ' ') AS nom, 
			stat, 
			team1, 
			team2, 
			date 
		ORDER BY stat DESC
		"""
	return gu.execute_query(logger, ctx, championship, "list", query, date=date, stat=str(stat).lower())


def get_best_day_matches(logger, ctx, championship, stat="gmsc", date=None):
	"""
	Function to get the best matches by date.
	"""
	date = str(datetime.today().strftime('%m%d')) if date is None else str(datetime.strptime(str(date), '%Y%m%d').strftime('%m%d'))
	query = """
		MATCH (game:Game WHERE toString(game.dat) =~ '[0-9]{4}'+$date) 
		WITH game 
		CALL (game) { 
			MATCH (team)-[:BOXSCORE]->(game)<-[r:PLAYS]-() 
			RETURN game.dat AS dat, collect(DISTINCT {shn: team.shn, nik: team.nik}) AS teams, round(sum(r[$stat]), 2) AS stat 
		} 
		RETURN 
			dat AS date, 
			CASE WHEN substring(game.gid, 9) = teams[0].shn THEN teams[0].nik ELSE teams[1].nik END AS team1, 
			CASE WHEN substring(game.gid, 9) <> teams[0].shn THEN teams[0].nik ELSE teams[1].nik END AS team2, 
			stat AS stat 
		ORDER BY stat DESC LIMIT 5
		"""
	return gu.execute_query(logger, ctx, championship, "list", query, date=date, stat=str(stat).lower())


def search(logger, ctx, championship, txt):
	"""
	Function that searchs for games (3 past game + 1 future game) for each team that starts with the text.
	"""
	result = []
	if (len(txt) >= 3 and len(txt) <= 35 and re.search('[a-z0-9 ]', txt, flags=re.IGNORECASE)):
		query = """
			CALL db.index.fulltext.queryNodes('fulltext_Game_description', $txt) 
			YIELD node 
			CALL (node) { 
				MATCH (home_team)-[:BOXSCORE]->(node)<-[:BOXSCORE]-(visitor_team) 
				WHERE node.gid =~ "(?i)[0-9]{9}"+home_team.shn 
				RETURN node.dat AS date, home_team.nik AS team1, visitor_team.nik AS team2, CASE WHEN node.played THEN 0 ELSE 1 END AS preview, 'Game' AS label 
			} 
			RETURN date, team1, team2, preview, label LIMIT 10
			"""
		result = gu.execute_query(logger, ctx, championship, "list", query, txt=txt)
	return result


def get_teams(logger, ctx, championship):
	"""
	Function to get teams.
	"""
	query = """
		MATCH (team:Team) 
		WHERE EXISTS((team)-[:BOXSCORE]->(:Game)-[:BELONGS_TO]->(:Season)) 
		RETURN collect(apoc.map.removeKeys(properties(team), ['div', 'cty', 'cnf']))
		"""
	data = gu.execute_query(logger, ctx, championship, "single", query)
	return data[0] if len(data) > 0 else []


def get_players(logger, ctx, championship):
	"""
	Function to get players.
	"""
	query = """
		MATCH (player:Player) 
		WHERE EXISTS((player)-[:PLAYS]->(:Game)-[:BELONGS_TO]->(:Season)) 
		RETURN collect({fn: player.fn, ln: player.ln, pid: player.pid})
		"""
	data = gu.execute_query(logger, ctx, championship, "single", query)
	return data[0] if len(data) > 0 else []


def get_nationalities(logger, ctx, championship):
	"""
	Function to get nationalities.
	"""
	query = """
		MATCH (player:Player) 
		RETURN collect(DISTINCT player.nat)
		"""
	data = gu.execute_query(logger, ctx, championship, "single", query)
	return data[0] if len(data) > 0 else []


def get_player_data(logger, ctx, championship, pid, date_start, date_end):
	"""
	Function to get player data.
	Replace nan values by 0 (bcl, 0, 19961101, 20220101)
	"""
	query = """
		MATCH (player:Player {pid: $pid}) 
		OPTIONAL MATCH (player)-[r:PLAYS]->(game)<-[:BOXSCORE]-(team:Team {tid: r.tid}) 
		WITH player, r, game, team 
		ORDER BY game.dat 
		WITH 
			player, team, 
			collect(game.dat) AS dats, 
			collect(CASE WHEN $date_start <= game.dat <= $date_end THEN r END) AS rs 
		WITH 
			player, 
			apoc.coll.sortMaps(collect(DISTINCT {nik: team.nik, tid: team.tid, start: dats[0], end: dats[-1]}), '^end') AS niks, 
			apoc.coll.flatten(collect(dats)) AS dats, apoc.coll.flatten(collect(rs)) AS rs 
		OPTIONAL MATCH (team:Team {tid: niks[-1].tid}) 
		WITH 
			player, team, dats, niks, rs, size(rs) AS nbMatches, [r IN rs | r.win] AS win, 
			[r IN rs | r.pie] AS pie, [r IN rs | r.pts] AS pts, [r IN rs | r.ast] AS ast, 
			[r IN rs | r.orb] AS orb, [r IN rs | r.drb] AS drb, [r IN rs | r.mp] AS mp, 
			[r IN rs | r.att] AS att, [r IN rs | r.usg] AS usg, [r IN rs | r.efgp] AS efgp, 
			[r IN rs | r.fg] AS fg, [r IN rs | r.fga] AS fga, [r IN rs | r.ft] AS ft, 
			[r IN rs | r.fta] AS fta, [r IN rs | r.twp] AS twp, [r IN rs | r.twpa] AS twpa, 
			[r IN rs | r.tp] AS tp, [r IN rs | r.tpa] AS tpa, [r IN rs | r.tov] AS tov, 
			[r IN rs | r.stl] AS stl, [r IN rs | r.pf] AS pf, [r IN rs | r.blk] AS blk, 
			[r IN rs | r.cm] AS cm, [r IN rs | r.ads] AS ads, [r IN rs | r.col] AS col, 
			[r IN rs | r.agr] AS agr, [r IN rs | r.oagr] AS oagr, [r IN rs | r.alt] AS alt, 
			[r IN rs | r.dpm] AS dpm, [r IN rs | r.orb+r.drb] AS rbd, [r IN rs | r.pm] AS pm, 
			[r IN rs | r.ftr] AS ftr, [r IN rs | r.orbp] AS orbp, [r IN rs | r.ff] AS ff, [r IN rs | r.tur] AS tur 
		WITH 
			player, team, dats, niks, rs, nbMatches, apoc.coll.sum(win) AS win, pie AS x, 
			round(apoc.coll.avg(pie), 1) AS pie, round(apoc.coll.avg(pts), 1) AS pts, round(apoc.coll.avg(ast), 1) AS ast, 
			round(apoc.coll.avg(orb), 1) AS orb, round(apoc.coll.avg(drb), 1) AS drb, round(apoc.coll.avg(mp), 1) AS mp, 
			round(apoc.coll.avg(att), 1) AS att, round(apoc.coll.avg(usg), 1) AS usg, round(apoc.coll.avg(efgp), 1) AS efgp, 
			round(apoc.coll.avg(fg), 1) AS fg, apoc.coll.sum(fg) AS fg_sum, apoc.coll.sum(fga) AS fga_sum, 
			apoc.coll.avg(ft) AS ft, apoc.coll.avg(fta) AS fta, apoc.coll.avg(twp) AS twp, 
			apoc.coll.avg(twpa) AS twpa,apoc.coll.avg(tp) AS tp, apoc.coll.avg(tpa) AS tpa, 
			round(apoc.coll.avg(tov), 1) AS tov, round(apoc.coll.avg(stl), 1) AS stl, round(apoc.coll.avg(pf), 1) AS pf, 
			round(apoc.coll.avg(blk), 1) AS blk, round(apoc.coll.avg(CASE WHEN 50 IN cm THEN [e in cm WHERE e <> 50 ] + [50] END), 1) AS cm, 
			round(apoc.coll.avg(ads), 1) AS ads, round(apoc.coll.avg(col), 1) AS col, round(apoc.coll.avg(agr), 1) AS agr, 
			round(apoc.coll.avg(oagr), 1) AS oagr, round(apoc.coll.avg(alt), 1) AS alt, round(apoc.coll.avg(dpm), 1) AS dpm, 
			round(apoc.coll.avg(rbd), 1) AS rbd, round(apoc.coll.avg(pm), 1) AS pm, round(apoc.coll.avg(ftr), 1) AS ftr, 
			round(apoc.coll.avg(orbp), 1) AS orbp, round(apoc.coll.avg(ff), 1) AS ff, round(apoc.coll.avg(tur), 1) AS tur
		RETURN 
			player.fn AS fn, 
			player.ln AS ln, 
			player.bth AS bth, 
			team.hcl AS hcl, 
			team.vcl AS vcl, 
			dats[0] AS start, 
			dats[-1] AS end, 
			niks, nbMatches, 
			CASE WHEN nbMatches <> 0 AND win <> 0 THEN round(win/nbMatches, 2) * 100 ELSE 0 END AS winPercentage, 
			x, pie, pts, ast, orb, drb, mp, att, usg, efgp, fg, 
			CASE WHEN fg_sum <> 0 AND fga_sum <> 0 THEN round(fg_sum/fga_sum*100, 1) ELSE 0 END AS fgp, 
			round(ft, 1) AS ft, 
			CASE WHEN ft <> 0 AND fta <> 0 THEN round(ft/fta*100, 1) ELSE 0 END AS ftp, 
			round(twp, 1) AS twp, 
			CASE WHEN twp <> 0 AND twpa <> 0 THEN round(twp/twpa*100, 1) ELSE 0 END AS twpp, 
			round(tp, 1) AS tp, 
			CASE WHEN tp <> 0 AND tpa <> 0 THEN round(tp/tpa*100, 1) ELSE 0 END AS tpp, 
			tov, stl, pf, blk, cm, ads, col, agr, oagr, alt, dpm, rbd, pm, ftr, orbp, ff, tur
		"""
	data = gu.execute_query(logger, ctx, championship, "list", query, pid=int(pid), date_start=int(date_start), date_end=int(date_end))
	result = {}
	if len(data) > 0:
		data = data[0]
		if data['nbMatches'] > 20:
			n = 20
			data['x'] = [round(sum(data['x'][i:i+n]) / n, 2) for i in range(0, len(data['x']), n)]
		result = data
	return result


def get_player_timeline(logger, ctx, championship, pid):
	"""
	Function to get player timeline.
	"""
	query = """
		MATCH (player:Player {pid: $pid}) 
		CALL (player) { 
			MATCH (player)-[r:PLAYS]->(game) 
			RETURN r.tid AS pTid, game, r.pts AS pts, r.ast AS ast, r.orb + r.drb AS rbd, r.gmsc AS gmsc, r.cm AS cm, r.blk AS blk, r.stl AS stl, 'pts' AS sort 
			ORDER BY pts DESC LIMIT 1 
			UNION ALL 
			MATCH (player)-[r:PLAYS]->(game) 
			RETURN r.tid AS pTid, game, r.pts AS pts, r.ast AS ast, r.orb + r.drb AS rbd, r.gmsc AS gmsc, r.cm AS cm, r.blk AS blk, r.stl AS stl, 'ast' AS sort 
			ORDER BY ast DESC LIMIT 1 
			UNION ALL 
			MATCH (player)-[r:PLAYS]->(game) 
			RETURN r.tid AS pTid, game, r.pts AS pts, r.ast AS ast, r.orb + r.drb AS rbd, r.gmsc AS gmsc, r.cm AS cm, r.blk AS blk, r.stl AS stl, 'blk' AS sort 
			ORDER BY blk DESC LIMIT 1 
			UNION ALL 
			MATCH (player)-[r:PLAYS]->(game) 
			RETURN r.tid AS pTid, game, r.pts AS pts, r.ast AS ast, r.orb + r.drb AS rbd, r.gmsc AS gmsc, r.cm AS cm, r.blk AS blk, r.stl AS stl, 'stl' AS sort 
			ORDER BY stl DESC LIMIT 1 
			UNION ALL 
			MATCH (player)-[r:PLAYS]->(game) 
			RETURN r.tid AS pTid, game, r.pts AS pts, r.ast AS ast, r.orb + r.drb AS rbd, r.gmsc AS gmsc, r.cm AS cm, r.blk AS blk, r.stl AS stl, 'rbd' AS sort 
			ORDER BY rbd DESC LIMIT 1 
			UNION ALL 
			MATCH (player)-[r:PLAYS {win: 1}]->(game) 
			RETURN r.tid AS pTid, game, r.pts AS pts, r.ast AS ast, r.orb + r.drb AS rbd, r.gmsc AS gmsc, r.cm AS cm, r.blk AS blk, r.stl AS stl, 'cm' AS sort 
			ORDER BY cm DESC LIMIT 1 
			UNION ALL 
			MATCH (player)-[r:PLAYS]->(game) 
			RETURN r.tid AS pTid, game, r.pts AS pts, r.ast AS ast, r.orb + r.drb AS rbd, r.gmsc AS gmsc, r.cm AS cm, r.blk AS blk, r.stl AS stl, 'gmsc' AS sort 
			ORDER BY gmsc DESC LIMIT 1 
			UNION ALL 
			MATCH (player)-[r:PLAYS]->(game) 
			WITH r.tid AS pTid, game, r.pts AS pts, r.ast AS ast, r.orb + r.drb AS rbd, r.gmsc AS gmsc, r.cm AS cm, r.blk AS blk, r.stl AS stl 
			ORDER BY game.dat ASC 
			WITH DISTINCT pTid, head(collect([game, pts, ast, rbd, gmsc, cm, blk, stl])) AS data 
			RETURN pTid, data[0] AS game, data[1] AS pts, data[2] AS ast, data[3] AS rbd, data[4] AS gmsc, data[5] AS cm, data[6] AS blk, data[7] AS stl, 'team' AS sort 
			UNION ALL 
			MATCH (player)-[r:PLAYS]->(game) 
			RETURN r.tid AS pTid, game, r.pts AS pts, r.ast AS ast, r.orb + r.drb AS rbd, r.gmsc AS gmsc, r.cm AS cm, r.blk AS blk, r.stl AS stl, 'last' AS sort 
			ORDER BY game.dat DESC LIMIT 1
		} 
		WITH pTid, game, pts, ast, rbd, gmsc, cm, blk, stl, sort 
		MATCH (home_team)-[r1:BOXSCORE]->(game)<-[r2:BOXSCORE]-(visitor_team) 
		WHERE game.gid =~ '(?i)[0-9]{9}'+home_team.shn 
		RETURN DISTINCT home_team.nik AS hTeam, visitor_team.nik AS vTeam, home_team.tid AS hTid, visitor_team.tid AS vTid, game.dat AS date, r1.pts AS hPts, r2.pts AS vPts, pTid, pts, ast, rbd, round(gmsc, 2) AS gmsc, round(cm, 2) AS cm, blk, stl, sort 
		ORDER BY date DESC
		"""
	return gu.execute_query(logger, ctx, championship, "list", query, pid=int(pid))


def get_player_games(logger, ctx, championship, pid, nb_matchs):
	"""
	Function to get player games.
	"""
	query = """
		MATCH (player:Player {pid: $pid}) 
		CALL (player) { 
			MATCH (player)-[r:PLAYS]->(game) 
			WITH game, r 
			ORDER BY game.dat DESC LIMIT $nb_matchs 
			MATCH (home_team)-[:BOXSCORE]->(game)<-[:BOXSCORE]-(visitor_team) 
			WHERE game.gid =~ '(?i)[0-9]{9}'+home_team.shn 
			RETURN {hTeam: home_team.nik, hShn: home_team.shn, vTeam: visitor_team.nik, vShn: visitor_team.shn, date: game.dat} AS game_info, r 
		} 
		RETURN collect(apoc.map.merge(game_info, properties(r)))
		"""
	return gu.execute_query(logger, ctx, championship, "single", query, pid=int(pid), nb_matchs=int(nb_matchs))[0]


def get_championships(logger, ctx, name=None):
	"""
	Function to get all championships.
	"""
	if name is not None:
		query = """
			MATCH (championship:Championship {shn: $name}) 
			RETURN collect(properties(championship))
			"""
		data = gu.execute_query(logger, ctx, "championships", "single", query, name=name)
		return data[0][0] if len(data) > 0 else {}
	else:
		query = """
			MATCH (championship:Championship) 
			RETURN collect(properties(championship))"""
		data = gu.execute_query(logger, ctx, "championships", "single", query)
		return data[0] if len(data) > 0 else []


def get_games(logger, ctx, championship, result_type):
	"""
	Function to get all matches (sitemap & picture).
	"""
	query = """
		MATCH (home_team)-[:BOXSCORE]->(game:Game 
			WHERE game.gid =~ '(?i)[0-9]{9}'+home_team.shn
		)<-[:BOXSCORE]-(visitor_team) 
		RETURN 
			home_team.nik AS n1, 
			visitor_team.nik AS n2, 
			game.dat AS dat 
		ORDER BY dat DESC
		"""
	return gu.execute_query(logger, ctx, championship, result_type, query)


def get_games_by_season(logger, ctx, championship, result_type, season):
	"""
	Function to get all matches by season (picture).
	"""
	query = """
		MATCH (home_team)-[:BOXSCORE]->(game:Game 
			WHERE game.played = true 
			AND game.gid =~ '(?i)[0-9]{9}'+home_team.shn 
			AND EXISTS { (game)-[:BELONGS_TO]->(:Season {season: $season}) }
		)<-[:BOXSCORE]-(visitor_team) 
		RETURN 
			home_team.nik AS n1, 
			visitor_team.nik AS n2, 
			game.dat AS dat 
		ORDER BY dat DESC
		"""
	return gu.execute_query(logger, ctx, championship, result_type, query, season=int(season))


def get_games_by_date(logger, ctx, championship, result_type, date):
	"""
	Function to get all matches by date (picture).
	"""
	query = """
		MATCH (home_team)-[:BOXSCORE]->(game:Game 
			WHERE game.dat = $date 
			AND game.gid =~ '(?i)[0-9]{9}'+home_team.shn
		)<-[:BOXSCORE]-(visitor_team) 
		RETURN 
			home_team.nik AS n1, 
			visitor_team.nik AS n2, 
			game.dat AS dat 
		ORDER BY dat DESC
		"""
	return gu.execute_query(logger, ctx, championship, result_type, query, date=int(date))


def get_players_seo(logger, ctx, championship, result_type):
	"""
	Function to get players for the SEO.
	"""
	query = """
		MATCH (player:Player) 
		RETURN 
			player.pid AS pid, 
			player.fn AS fn, 
			player.ln AS ln 
		ORDER BY pid
		"""
	return gu.execute_query(logger, ctx, championship, result_type, query)


def get_newsletter_game_report_by_team(logger, ctx, championship, result_type, date):
	"""
	Function to get all matches report by date (report).
	"""
	query = """
		WITH $date AS d 
		MATCH (season:Season) 
		WITH d, season.start AS start 
		ORDER BY start DESC LIMIT 1 
		WITH d, start 
		MATCH (current_team)-[r1:BOXSCORE]->(game:Game WHERE game.dat = d AND game.played = true)<-[:BOXSCORE]-(other_team) 
		WITH d, start, current_team, other_team, r1, game 
		CALL (game, current_team, other_team) { 
			MATCH (game)<-[r3:PLAYS]-(player) 
			RETURN {fn: player.fn, ln: player.ln, tid: toInteger(r3.tid), team: CASE WHEN r3.tid = current_team.tid THEN current_team.nik ELSE other_team.nik END, pie: round(r3.pie, 2), ast: toInteger(r3.ast), tov: toInteger(r3.tov), att: round(r3.att, 2), usg: round(r3.usg, 2), piepm: round(r3.piepm, 2), mp: toInteger(round(r3.mp)), cm: round(r3.cm, 2)} AS player_data 
		} 
		WITH d, start, current_team, other_team, r1, game, player_data 
		CALL (d, start, current_team) { 
			MATCH (current_team)-[r:BOXSCORE]->(game:Game WHERE start <= game.dat <= d AND game.played = true) 
			WITH game.dat AS date, r.win AS win 
			ORDER BY date 
			RETURN collect(win) AS win 
		} 
		RETURN 
			d AS date, 
			CASE WHEN game.gid =~ '(?i)[0-9]{9}'+current_team.shn THEN current_team.nik ELSE other_team.nik END AS home, 
			CASE WHEN game.gid =~ '(?i)[0-9]{9}'+current_team.shn THEN other_team.nik ELSE current_team.nik END AS visitor, 
			current_team.fra AS current_team_fra, 
			other_team.fra AS other_team_fra, 
			current_team.tid AS tid, 
			collect(player_data) AS player_data, 
			r1.lt AS lt, 
			toInteger(r1.lc) AS lc, 
			toInteger(r1.eq) AS eq, 
			round(r1.tie, 2) AS tie, 
			round(r1.pace, 2) AS pace, 
			round(r1.pos, 2) AS pos, 
			round(r1.ff, 2) AS ff, 
			round(r1.afgp, 2) AS afgp, 
			toInteger(r1.dp) AS dp, 
			win
		"""
	return gu.execute_query(logger, ctx, championship, result_type, query, date=int(date))


def get_common_periods(mp, periods, algo):
	"""
	Function to get the common periods of time for a group of periods.
	"""
	result = []
	cols = range(0, len(periods))
	# Create a dataframe where each column represent a player and each index a second during the game
	df = pd.DataFrame(False, columns=cols, index=list(range(0, (int(mp)*60)+1)))
	# For each period
	for i in cols:
		# Get the list of period of a player
		l = iter(periods[i])
		# Fill the DataFrame with True values for each second the player played
		for deb, end in zip(l, l):
			df.loc[deb:end, i] = True
	# Get rows full of True values
	if algo == "all":
		df = df[(df == True).all(axis=1)]
	# Get rows which contains at least one True value
	else:
		df = df[(df == True).any(axis=1)]
	# Split a list of integers if they are none consecutive then get ranges
	for _, g in groupby(enumerate(list(df.index)), lambda i_x: i_x[0] - i_x[1]):
		tmp = list(map(itemgetter(1), g))
		result.append([tmp[0], tmp[-1]])
	return result


def get_boxscore_by_pbp(teams, players, pbp, periods):
	"""
	Function to get boxscore by play-by-play and periods.
	"""
	# Get boxscore during period
	boxscore = pd.DataFrame(0, columns=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 18, 19], index=teams)
	# For each event
	for play_id, player_id, play_time in zip(pbp[0], pbp[1], pbp[2]):
		try:
			# If event occurs during one of the period
			if (any((period[0] <= play_time <= period[1]) > 0 for period in periods)) & (not play_id in [15, 16, 17]):
				# Add the action to the right team
				boxscore.loc[players[str(player_id)], play_id] += 1
		except:
			continue
	boxscore[20] = sum([period[1] - period[0] for period in periods])
	return boxscore


def get_play_by_play_boxscore(logger, ctx, championship, players, teams, periods, dates, matches, players_list):
	"""
	Function to get boxscore.
	"""
	result = []
	res_players = {}
	# Check teams parameter
	where_clause_teams = "("+" OR ".join(["team.nik =~ '(?i)"+nik+"'" for nik in teams])+")"
	# Check dates parameter
	where_clause_dates = "AND $start <= game.dat <= $end " if len(dates) == 2 and dates[0] <= dates[1] and all(isinstance(date, int) for date in dates) else ""
	start = (dates[0] if len(dates) == 2 else None)
	end = (dates[1] if len(dates) == 2 else None)
	# Check matches parameter
	matches = matches if matches is not None and 0 < matches <= 40 else 40
	# Build common query
	query_common = """
		MATCH (team)-[r:BOXSCORE]->(game:Game {played: true}) 
		WHERE """+where_clause_teams+""" """+where_clause_dates+"""
		WITH team, {mp: r.mp, gid: game.gid} AS item 
		ORDER BY game.dat 
		WITH team, collect(item)[-$matches..] AS items 
		UNWIND items AS item 
		WITH DISTINCT item 
		MATCH (player)-[r:PLAYS {tid: team.tid}]->(game:Game {gid: item.gid})<-[:BOXSCORE]-(team) 
		"""
	# Build query to get games
	query_games = query_common + """
		RETURN 
			item.gid AS gid, 
			game.pbp AS pbp, 
			item.mp AS mp, 
			collect(CASE WHEN player.pid IN $players THEN r.prds END) AS periods, 
			apoc.map.fromLists(collect(toString(player.pid)), collect(team.nik)) AS players, 
			collect(DISTINCT team.nik) AS teams
		"""
	# Build query to get players
	if players_list:
		query_players = query_common + """
			WITH team.nik AS nik, collect(DISTINCT {pid: player.pid, fn: player.fn, ln: player.ln}) AS players 
			RETURN apoc.map.mergeList(collect(apoc.map.setKey({}, nik, players))) AS players
			"""
		res_players = gu.execute_query(logger, ctx, championship, "single", query_players, teams=teams, start=start, end=end, matches=matches)[0]
	# Execute the query
	items = gu.execute_query(logger, ctx, championship, "list", query_games, teams=teams, start=start, end=end, matches=matches, players=players)
	# For each team create an index and an opponent index
	indexes = teams + ["opp"+str(team) for team in teams]
	tmp = {str(key): [] for key in indexes}
	# For each game
	for item in items:
		if len(players) == len(item["periods"]):
			# If periods parameter filled and players parameter not filled
			if periods and not item["periods"]:
				prds = get_common_periods(item["mp"], periods, "any")
			# If periods parameter filled and players parameter filled
			elif periods and item["periods"]:
				# Add periods parameter to the list of player periods 
				item["periods"].extend([[i for j in periods for i in j]])
				prds = get_common_periods(item["mp"], item["periods"], "all")
			else:
				prds = get_common_periods(item["mp"], item["periods"], "all")
			# Get seconds played during the periods
			seconds = sum([period[1] - period[0] for period in prds])
			# Format play-by-play as DataFrame
			report_pbp = pbp.get_format_pbp(item["pbp"], "df")[[0, 1, 2]]
			# Get boxscore for the computed periods
			boxscore = get_boxscore_by_pbp(item["teams"], item["players"], report_pbp, prds)
			if len(boxscore.index) > 0:
				# Rename boxscore columns
				boxscore.rename(columns=pbp.ACTIONS, inplace=True)
				# Compute team statistics
				boxscore = pbp.compute_statistics(boxscore, "team")
				boxscore["mp"] = seconds
				# For each row of the boxscore
				for i in range(0, len(boxscore.index)):
					# Get index
					index = str(boxscore.index[i])
					if index in tmp:
						opp_index = "opp"+index
						# Add the other boxscore row to the opponent index
						tmp[opp_index].append(boxscore.loc[boxscore.index[1-i]].to_dict())
						# Add the boxscore row to the index team
						tmp[index].append(boxscore.loc[boxscore.index[i]].to_dict())
	# For each team
	for key in tmp:
		# Each row represents a game
		tmp[key] = pd.DataFrame(tmp[key])
		# Compute the mean to only get one row
		tmp[key] = tmp[key].mean().round(1)
		tmp[key]["mp"] = round(tmp[key]["mp"] / 60)
		if "opp" in key:
			# Keep only four factors statistics for opponent index and 
			tmp[key] = tmp[key][["efgp", "tur", "drbp", "ftr", "ff"]].rename(index={"efgp": "opp_efgp", "tur": "opp_tur", "drbp": "opp_drbp", "ftr": "opp_ftr", "ff": "opp_ff"})
			# Merge four factors statistics the boxscore
			tmp[key[3:]] = pd.concat([tmp[key[3:]], tmp[key]], axis=0)
			tmp_res = {**tmp[key[3:]].to_dict(), "nik": key[3:]}
			# Add players if asked
			if players_list:						
				tmp_res["players"] = res_players[key[3:]]
			# Add the completed boxscore
			result.append(tmp_res)
	return result
