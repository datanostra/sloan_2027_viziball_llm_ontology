#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from matplotlib import pyplot
import app.graph.connector as gc
import app.graph.util as gu


def get_best_performance_by_date(logger, ctx, championship, list_date, limit, stat):
	"""
	Function to get the best performances by dates.
	"""
	list_date = map(int, list_date)
	query = "MATCH (t1:Team)-[:BOXSCORE]->(g:Game)<-[:BOXSCORE]-(t2:Team) WHERE g.played = true AND g.dat IN $list_date AND g.gid =~ '(?i)[0-9]{9}'+t1.shn WITH g, $stat AS stat, t1.nik AS team1, t2.nik AS team2 CALL (g, stat) { MATCH (g)-[r:PLAYS]-(p:Player) RETURN p.ln AS lastname, p.fn AS firstname, round(max(r[stat]), 2) AS max ORDER BY max DESC LIMIT 1 } RETURN firstname + ' ' + lastname AS player, left(g.gid, 4) AS year, max AS stat, 'https://viziball.app/game/'+$championship+'/fr/' + toLower(team1) + '/' + toLower(team2) + '/' + left(g.gid, 8) AS match ORDER BY stat DESC LIMIT $limit"
	return gu.execute_query(logger, ctx, championship, "df", query, championship=str(championship).lower(), list_date=list_date, limit=int(limit), stat=str(stat).lower())


def get_best_performance_by_game(logger, ctx, championship, list_game, limit, stat):
	"""
	Function to get the best performances by games.
	"""
	query = "MATCH (t1:Team)-[:BOXSCORE]->(g:Game)<-[:BOXSCORE]-(t2:Team) WHERE g.played = true AND g.gid IN $list_game AND g.gid =~ '(?i)[0-9]{9}'+t1.shn WITH g, $stat AS stat, t1.nik AS team1, t2.nik AS team2 CALL (g, stat) { MATCH (g)-[r:PLAYS]-(p:Player) RETURN p.ln AS lastname, p.fn AS firstname, round(max(r[stat]), 2) AS max ORDER BY max DESC LIMIT 1 } RETURN firstname + ' ' + lastname AS player, left(g.gid, 4) AS year, max AS stat, 'https://viziball.app/game/'+$championship+'/fr/' + toLower(team1) + '/' + toLower(team2) + '/' + left(g.gid, 8) AS match ORDER BY stat DESC LIMIT $limit"
	return gu.execute_query(logger, ctx, championship, "df", query, championship=str(championship).lower(), list_game=list_game, limit=int(limit), stat=str(stat).lower())


def get_best_performance(logger, ctx, championship, limit, stat):
	"""
	Function to get the best performances.
	"""
	query = "MATCH (t1:Team)-[:BOXSCORE]->(g:Game)<-[:BOXSCORE]-(t2:Team) WHERE g.played = true AND g.gid =~ '(?i)[0-9]{9}'+t1.shn WITH g, $stat AS stat, t1.nik AS team1, t2.nik AS team2 CALL (g, stat) { MATCH (g)-[r:PLAYS]-(p:Player) RETURN p.ln AS lastname, p.fn AS firstname, round(max(r[stat]), 2) AS max ORDER BY max DESC LIMIT 1 } RETURN firstname + ' ' + lastname AS player, left(g.gid, 4) AS year, max AS stat, 'https://viziball.app/game/'+ $championship+'/fr/' + toLower(team1) + '/' + toLower(team2) + '/' + left(g.gid, 8) AS match ORDER BY stat DESC LIMIT $limit"
	return gu.execute_query(logger, ctx, championship, "df", query, championship=str(championship).lower(), limit=int(limit), stat=str(stat).lower())


def get_best_team_squad(logger, ctx, championship, season, nb_players=13):
	"""
	Function to find the best team squad by teams for a season.
	"""
	query = "MATCH (s:Season {season: $season}) WITH s MATCH (t1:Team)-[r1:BOXSCORE]->(g:Game)<-[r2:BOXSCORE]-(t2:Team) WHERE g.played = true AND EXISTS((g)-[:BELONGS_TO]->(s)) AND g.gid =~ '(?i)[0-9]{9}'+t1.shn WITH g.gid AS gid, t1.tid AS tid, t1.nik AS nik, t1.shn AS shn, r1.win AS win CALL (gid, tid) { MATCH (g:Game {gid: gid})<-[r:PLAYS {tid: tid}]-(p:Player) WITH apoc.text.join([p.fn, p.ln], ' ') AS player, r.mp AS mp ORDER BY mp DESC LIMIT $nb_players RETURN collect(player) AS players } RETURN gid, tid, shn, nik, win, players"
	df = gu.execute_query(logger, ctx, championship, "df", query, season=int(season), nb_players=int(nb_players))
	df['players'] = [', '.join(sorted(x)) for x in df['players']]
	tmp = df['players'].value_counts().sort_index(ascending=True)
	df = df[df.columns.difference(['gid'])].groupby(['players', 'tid', 'shn', 'nik'], as_index=False).sum()
	df.sort_values(by=['players'], ascending=False, inplace=True)
	df['lose'] = tmp.values
	df['winPercentage'] = round((df['win'] * 100) / (df['win'] + df['lose']), 2)
	df.sort_values(by=['winPercentage'], ascending=False, inplace=True)
	df.reset_index(drop=True, inplace=True)
	return df


def get_win_percentage_players(logger, ctx, championship, season):
	"""
	Function to get the percentage of wins for each player.
	"""
	query = "MATCH (p:Player)-[r:PLAYS]->(g:Game)-[:BELONGS_TO]->(s:Season {season: $season}) WITH p.fn AS fn, p.ln AS ln, toFloat(sum(r.win)) / count(g) * 100 AS winPercentage, round(avg(r.mp), 2) AS mp RETURN *  ORDER BY winPercentage DESC, mp DESC"
	return gu.execute_query(logger, ctx, championship, "df", query, season=int(season))


def get_best_performance_by_player(logger, ctx, championship, fn, ln, stat, limit):
	"""
	Function to get the best performances for a player.
	"""
	query = "MATCH (p:Player)-[r:PLAYS]->(g:Game) WHERE p.fn =~ '(?i)'+$fn AND p.ln =~ '(?i)'+$ln WITH g, r[$stat] AS stat ORDER BY stat DESC LIMIT $limit CALL (g) { MATCH (t1:Team)-[:BOXSCORE]->(g)<-[:BOXSCORE]-(t2:Team) WHERE g.gid =~ \"(?i)[0-9]{9}\"+t1.shn RETURN 'https://viziball.app/game/'+$championship+'/fr/' + toLower(t1.nik) + '/' + toLower(t2.nik) + '/' + left(g.gid, 8) AS match LIMIT 1 } RETURN stat, match"
	return gu.execute_query(logger, ctx, championship, "df", query, championship=str(championship).lower(), fn=str(fn), ln=str(ln), stat=str(stat).lower(), limit=int(limit))


def get_stat_ranking(logger, ctx, championship, date_start, date_end):
	"""
	Function to gets the ranking of statistics during a period.
	"""
	# Get stat keys
	query = "MATCH (:Team)-[r:BOXSCORE]->(g:Game) RETURN keys(r) LIMIT 1"
	stats = gu.execute_query(logger, ctx, championship, "single", query)[0]
	stats = [s for s in stats if s not in ['mp', 'win']]
	# Get stat ranking
	df = pd.DataFrame(columns=['stat', 'corr'])
	for stat in stats:
		res = pd.DataFrame(gc.get_team_ranking(logger, ctx, championship=championship, date_start=str(date_start), date_end=str(date_end), stat=stat, limit=30, operator="avg", sort="DESC", p_min=0, p_max=100))
		df = df.append({"stat": stat, "corr": res[[stat, "winPercentage"]].corr().iloc[0, 1]}, ignore_index=True)
	df.sort_values(by='corr', inplace=True, ascending=False)
	df.reset_index(inplace=True, drop=True)
	return df


def get_team_stat_matrix(logger, ctx, championship):
	"""
	Function to gets the team stat matrix.
	"""
	# Get stat keys
	query = "MATCH (:Team)-[r:BOXSCORE]->(g:Game) RETURN keys(r) LIMIT 1"
	stats = gu.execute_query(logger, ctx, championship, "single", query)[0]
	stats = [s for s in stats if s not in ['tid', 'dist', 'rd', 'win']]
	# Get teams id
	query = "MATCH (n:Team) RETURN collect(n.tid), collect(n.fra)"
	tid, fra = gu.execute_query(logger, ctx, championship, "single", query)
	# Get season date
	query = "MATCH (n:Season) RETURN n.season AS season, n.start AS date_start, n.end AS date_end"
	seasons = gu.execute_query(logger, ctx, championship, "df", query)
	# Init matrix
	matrix = pd.DataFrame(0, index=stats, columns=tid)
	# For each season
	for row in seasons.itertuples():
		# For each stat
		for stat in stats:
			# Compute player ranking
			res = pd.DataFrame(gc.get_team_ranking(logger, ctx, championship=championship, date_start=int(row.date_start), date_end=int(row.date_end), stat=stat, limit=1, 
			operator="avg", sort="ASC", p_min=0, p_max=100))
			if len(res.index) > 0:
				matrix.loc[stat, res["tid"].iloc[0]] += 1
	# Replace column names with franchise
	matrix.columns = fra
	return matrix


def get_50_40_90_ranking(logger, ctx, championship, season):
	"""
	Function to get the 50–40–90 club ranking for a season.
	"""
	query = "MATCH (s:Season {season: $season}) WITH s MATCH (p:Player)-[r:PLAYS]->(g:Game)-[:BELONGS_TO]->(s) WHERE g.played = true WITH p.fn AS fn, p.ln AS ln, sum(r.fg) AS fg, sum(r.fga) AS fga, sum(r.tp) AS tp, sum(r.tpa) AS tpa, sum(r.ft) AS ft, sum(r.fta) AS fta WHERE fg >= 300 AND tp >= 82 AND ft >= 125 WITH fn, ln, fg, fga, tp, tpa, ft, fta, fg/fga*100 AS fgp, tp/tpa*100 AS tpp, ft/fta*100 AS ftp  WHERE fgp >= 50 AND tpp >= 40 AND ftp >= 90 RETURN fn, ln, fg, fga, tp, tpa, ft, fta, fgp, tpp, ftp ORDER BY fgp DESC, tpp DESC, ftp DESC"
	return gu.execute_query(logger, ctx, championship, "df", query, season=int(season))


def get_progression_by_player(logger, ctx, championship, season, nb_matchs=1, sort="DESC"):
	"""
	Function to get the progression of players between 2 seasons.
	"""
	query = "MATCH (s:Season {season: $season}) WITH s MATCH (p:Player)-[r:PLAYS]->(g:Game)-[:BELONGS_TO]->(s) WITH p, avg(r.pie) AS pie1, s, count(g) AS matches WHERE matches >= $nb_matchs WITH * CALL (p, s) { MATCH (p)-[r:PLAYS]->(g:Game)-[:BELONGS_TO]->(:Season {season: s.season-1}) WITH avg(r.pie) AS pie2, count(g) AS matches WHERE matches >= 25 RETURN pie2 } WITH p.fn + ' ' + p.ln AS player, pie1 - pie2 AS evolution ORDER BY evolution "+str(sort).upper()+" WHERE evolution IS NOT NULL RETURN player, evolution"
	return gu.execute_query(logger, ctx, championship, "df", query, season=int(season), nb_matchs=int(nb_matchs))


def get_progression_by_player_period(logger, ctx, championship, date_start1, date_end1, date_start2, date_end2, sort="DESC"):
	"""
	Function to get the progression of players between 2 defined periods.
	"""
	query = "MATCH (p:Player)-[r:PLAYS]->(g:Game) WHERE g.dat >= $date_start1 AND g.dat <= $date_end1 WITH p, avg(r.pie) AS pie1, $date_start2 AS date_start2, $date_end2 AS date_end2 CALL (p, date_start2, date_end2) { MATCH (p)-[r:PLAYS]->(g:Game) WHERE g.dat >= date_start2 AND g.dat <= date_end2 RETURN avg(r.pie) AS pie2 } WITH p.fn + ' ' + p.ln AS player, pie1 - pie2 AS evolution ORDER BY evolution "+str(sort).upper()+" WHERE evolution IS NOT NULL RETURN player, evolution"
	return gu.execute_query(logger, ctx, championship, "df", query, date_start1=int(date_start1), date_end1=int(date_end1), date_start2=int(date_start2), date_end2=int(date_end2))


def get_best_rookie(logger, ctx, championship, season, sort="DESC"):
	"""
	Function to get the best rookies of the season.
	"""
	query = "MATCH (p:Player)-[r:PLAYS]->(g:Game)-[:BELONGS_TO]->(s:Season) WITH p.fn AS fn, p.ln AS ln, avg(r.pie) AS pie, avg(r.pts) AS pts, avg(r.orb + r.drb) AS rb, avg(r.ast) AS ast, avg(r.stl) AS stl, avg(r.blk) AS blk, avg(r.fgp) AS fgp, avg(r.tpp) AS tpp, collect(DISTINCT s.season) AS seasons WHERE size(seasons) = 1 AND seasons[0] = $season RETURN fn, ln, pie, pts, rb, ast, stl, blk, fgp, tpp ORDER BY pie "+str(sort).upper()
	return gu.execute_query(logger, ctx, championship, "df", query, season=season)


def objective(x, a, b, c):
	return a * x + b * x**2 + c


def plot_graph(fra, x_values, y_values, labels):
	x = np.linspace(0, max(x_values)+1)
	popt, _ = curve_fit(objective, x_values, y_values)
	a, b, c = popt
	pyplot.scatter(x_values, y_values)
	x_line = np.arange(min(x), max(x), 1)
	y_line = objective(x_line, a, b, c)
	pyplot.plot(x_line, y_line, '--', color='red', label='y = %.5f * x + %.5f * x^2 + %.5f' % (a, b, c))
	pyplot.title(fra)
	pyplot.ylabel('Player Impact Estimate')
	pyplot.xlabel('Players')
	pyplot.yticks(np.arange(0, 21, 2.0))
	pyplot.xticks(np.arange(min(x_values), max(x_values)+1, 1.0), labels=labels, rotation=45)
	for i, v in enumerate(y_values):
		pyplot.annotate(str(round(v, 2)), xy=(i,v), xytext=(-7,7), textcoords='offset points')
	pyplot.legend(loc="upper right")
	pyplot.savefig('data/draft/coef/'+fra+'.png', bbox_inches='tight')
	pyplot.clf()


def save(data):
	coefs = []
	for record in data:
		df = pd.DataFrame(record['players'])
		df.sort_values(by='id', inplace=True, ascending=True, ignore_index=True)
		ids, pies = list(df['id']), list(df['pie'])
		plot_graph(record['fra'], ids, pies, list(df['name']))
		coefs.append(gc.linear_regression(pies)[0])
	data = pd.DataFrame(data)
	data['coef'] = coefs
	data.sort_values(by='coef', inplace=True, ascending=True, ignore_index=True)
	data[['fra', 'coef']].to_csv('data/draft/coef/coefs.csv', index=False)


def get_team_coefficient_by_season(logger, ctx, championship, season, mp=5):
	"""
	Function to get the team coefficient.
	"""
	query = "MATCH (s:Season {season: $season}) WITH s MATCH (t:Team)-[r:BOXSCORE]->(g:Game)-[:BELONGS_TO]->(s) WHERE g.played = true WITH DISTINCT t.tid AS tid, t.fra AS fra, collect(g.gid) AS gids, $mp AS mp CALL (gids, tid, mp) { MATCH (g:Game)<-[r:PLAYS {tid: tid}]-(p:Player) WHERE g.gid IN gids WITH p.pid AS pid, p.fn + ' ' + p.ln AS name, avg(r.pie) AS pie, avg(r.mp) AS mp ORDER BY pie WHERE mp >= mp WITH collect(pie) AS pies, collect(name) AS players RETURN pies, players, reverse(range(0, size(players)-1)) AS ids } RETURN fra, [x IN range(0, size(players)-1) | {name: players[x], pie: pies[x], id: ids[x]}] AS players"
	return gu.execute_query(logger, ctx, championship, "list", query, season=int(season), mp=float(mp))


def get_team_coefficient_by_period(logger, ctx, championship, date_start, date_end, mp=5):
	"""
	Function to get the team coefficient.
	"""
	query = "MATCH (t:Team)-[r:BOXSCORE]->(g:Game) WHERE g.played = true AND g.dat >= $date_start AND g.dat <= $date_end WITH DISTINCT t.tid AS tid, t.fra AS fra, collect(g.gid) AS gids, $mp AS mp CALL (gids, tid, mp) { MATCH (g:Game)<-[r:PLAYS {tid: tid}]-(p:Player) WHERE g.gid IN gids WITH p.pid AS pid, p.fn + ' ' + p.ln AS name, avg(r.pie) AS pie, avg(r.mp) AS mp ORDER BY pie WHERE mp >= mp WITH collect(pie) AS pies, collect(name) AS players RETURN pies, players, reverse(range(0, size(players)-1)) AS ids } RETURN fra, [x IN range(0, size(players)-1) | {name: players[x], pie: pies[x], id: ids[x]}] AS players"
	return gu.execute_query(logger, ctx, championship, "list", query, date_start=int(date_start), date_end=int(date_end), mp=float(mp))


def set_search_field(logger, ctx, championship, list_games=None):
	"""
	Function to set search field on Game nodes.
	"""
	check_gid = "AND g.gid IN $list_games " if list_games is not None else ""
	query = "CALL apoc.periodic.iterate('MATCH (t1:Team)-[:BOXSCORE]->(g:Game)<-[:BOXSCORE]-(t2:Team) WHERE g.gid =~ \"(?i)[0-9]{9}\"+t1.shn "+check_gid+"RETURN t1, g, t2', 'SET g:Search, g.search = apoc.text.join([toString(g.dat), t1.fra, t1.shn, t2.fra, t2.shn], \" \")', {batchSize: 1000, params: {list_games: $list_games}})"
	gu.execute_query(logger, ctx, championship, "None", query, list_games=list_games)


def get_player_value_statistic_win_percentage(logger, ctx, championship, pid, stat, value, date_start, date_end):
	"""
	Function to get the percentage of victory based on the value of a player's statistic
	"""
	query = "MATCH (:Player {pid: $pid})-[r:PLAYS]->(g:Game {played: True}) WHERE g.dat >= $date_start AND g.dat <= $date_end WITH collect(CASE WHEN r[$stat] >= $value THEN r.win END) AS s, collect(CASE WHEN r[$stat] < $value THEN r.win END) AS i RETURN apoc.coll.sum(s) / size(s) * 100 AS top, apoc.coll.sum(i) / size(i) * 100 AS bot"
	return gu.execute_query(logger, ctx, championship, "list", query, pid=int(pid), stat=stat, value=float(value), date_start=int(date_start), date_end=int(date_end))
