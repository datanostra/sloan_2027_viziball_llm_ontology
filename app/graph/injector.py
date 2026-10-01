#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
import os
import time
import app.util as util
import app.graph.util as gu


def create_database(logger, ctx, championship):
	"""
	Function to get the list of databases.
	"""
	start_time = time.time()
	
	championship = str(championship).lower()
	gu.execute_query(logger, ctx, "system", None, ("CREATE DATABASE "+championship+" IF NOT EXISTS"))

	logger.info("%s :: %s :: CREATE_DATABASE :: %s", os.path.basename(__file__), os.getpid(), util.get_duration(start_time))


def create_constraints_indexes(logger, ctx, championship):
	"""
	Function to create if possible uniqueness constraints an indexes on nodes.
	"""
	start_time = time.time()

	queries = None
	if championship.casefold() == "championships":
		queries = [
			"CREATE CONSTRAINT constraint_shn IF NOT EXISTS FOR (n:Championship) REQUIRE n.shn IS UNIQUE"
		]
	else:
		queries = [
			"CREATE CONSTRAINT constraint_Season IF NOT EXISTS FOR (n:Season) REQUIRE n.season IS UNIQUE",
			"CREATE CONSTRAINT constraint_Game IF NOT EXISTS FOR (n:Game) REQUIRE n.gid IS UNIQUE",
			"CREATE CONSTRAINT constraint_Team IF NOT EXISTS FOR (n:Team) REQUIRE n.tid IS UNIQUE",
			"CREATE CONSTRAINT constraint_Player IF NOT EXISTS FOR (n:Player) REQUIRE n.pid IS UNIQUE",
			"CREATE CONSTRAINT constraint_Event IF NOT EXISTS FOR (n:Event) REQUIRE n.id IS UNIQUE",
			"CREATE RANGE INDEX index_Game_dat IF NOT EXISTS FOR (n:Game) ON (n.dat)",
			"CREATE TEXT INDEX index_Team_nik IF NOT EXISTS FOR (n:Team) ON (n.nik)",
			"CREATE TEXT INDEX index_Team_shn IF NOT EXISTS FOR (n:Team) ON (n.shn)",
			"CREATE FULLTEXT INDEX fulltext_Game_description IF NOT EXISTS FOR (n:Game) ON EACH [n.description]"
		]
	if queries is not None:
		for query in queries:
			gu.execute_query(logger, ctx, championship, None, query)

	logger.info("%s :: %s :: CREATE_CONSTRAINTS_INDEXES :: %s :: %s", os.path.basename(__file__), os.getpid(), championship, util.get_duration(start_time))


def delete_games(logger, ctx, championship, date, operator):
	"""
	Function to remove non-played games.
	"""
	start_time = time.time()

	result = 0
	if operator in [">", "<", ">=", "<=", "="]:
		query = """
			MATCH (game:Game) 
			WHERE game.dat """+operator+""" $date 
			CALL (game) { 
				DETACH DELETE game 
			} IN TRANSACTIONS OF 1000 ROWS 
			RETURN count(game) AS deleted_games
			"""
		result = gu.execute_query(logger, ctx, championship, "single", query, date=int(date))[0]
	
	logger.info("%s :: %s :: DELETE_GAMES :: %s :: %s :: %s :: %s :: %s", os.path.basename(__file__), os.getpid(), championship, date, operator, result, util.get_duration(start_time))


def merge_batch_nodes(logger, ctx, championship, batch, node_class):
	"""
	Function which allows to add nodes contained in a batch.
	"""
	node_class = str(node_class).title()
	query = None
	if championship.casefold() == "championships":
		if node_class == "Championship":
			query = """
				UNWIND $batch AS row 
				MERGE (a:Championship {shn: row.shn}) 
				SET a += row
				"""
		else:
			pass
	else:
		if node_class == "Season":
			query = """
				UNWIND $batch AS row 
				MERGE (a:Season {season: row.season}) 
				SET a += row
				"""
		elif node_class == "Game":
			query = """
				UNWIND $batch AS row 
				MERGE (a:Game {gid: row.gid}) 
				SET a += row
				"""
		elif node_class == "Team":
			query = """
				UNWIND $batch AS row 
				MERGE (a:Team {tid: row.tid}) 
				SET a += row
				"""
		elif node_class == "Player":
			query = """
				UNWIND $batch AS row 
				MERGE (a:Player {pid: row.pid}) 
				SET a += row
				"""
		elif node_class == "Event":
			query = """
				UNWIND $batch AS row 
				MERGE (a:Event {id: row.id}) 
				SET a += row
				"""
		else:
			pass
	if query is not None:
		gu.execute_query(logger, ctx, championship, None, query, batch=batch)


def merge_batch_relationships(logger, ctx, championship, batch, node_class_1, node_class_2):
	"""
	Function which makes it possible to create relations between two nodes contained in a batch.
	"""
	node_class_1 = str(node_class_1).title()
	node_class_2 = str(node_class_2).title()
	query = None
	if node_class_1 == "Game" and node_class_2 == "Season":
		query = """
			UNWIND $batch AS row 
			MATCH (a:Game {gid: row.gid}) 
			MATCH (b:Season {season: row.season}) 
			MERGE (a)-[:BELONGS_TO]->(b)
			"""
	elif node_class_1 == "Player" and node_class_2 == "Game":
		query = """
			UNWIND $batch AS row 
			MATCH (a:Player {pid: row.pid}) 
			MATCH (b:Game {gid: row.gid}) 
			MERGE (a)-[r:PLAYS]->(b) 
			SET r += apoc.map.removeKeys(row, ['pid', 'gid'])
			"""
	elif node_class_1 == "Team" and node_class_2 == "Game":
		query = """
			UNWIND $batch AS row 
			MATCH (a:Team {tid: row.tid}) 
			MATCH (b:Game {gid: row.gid}) 
			MERGE (a)-[r:BOXSCORE]->(b) 
			SET r += apoc.map.removeKeys(row, ['tid', 'gid'])
			"""
	elif node_class_1 == "Event" and node_class_2 == "Game":
		query = """
			UNWIND $batch AS row 
			MATCH (a:Event {id: row.id}) 
			MATCH (b:Game {gid: row.gid}) 
			MERGE (a)-[r:OCCURS_IN]->(b) 
			SET r += apoc.map.removeKeys(row, ['id', 'gid'])
			"""
	elif node_class_1 == "Player" and node_class_2 == "Event":
		query = """
			UNWIND $batch AS row 
			MATCH (a:Player {pid: row.id_source}) 
			MATCH (b:Event {id: row.id}) 
			CALL apoc.merge.relationship(
				a, 
				row.action_libelle, 
				{id: row.id_rel}, 
				apoc.map.removeKeys(row, ['id_source', 'id', 'id_rel']), 
				b, 
				apoc.map.removeKeys(row, ['id_source', 'id', 'id_rel'])
			) 
			YIELD rel 
			RETURN rel
			"""
	elif node_class_1 == "Team" and node_class_2 == "Event":
		query = """
			UNWIND $batch AS row 
			MATCH (a:Team {tid: row.id_source}) 
			MATCH (b:Event {id: row.id}) 
			CALL apoc.merge.relationship(
				a, 
				row.action_libelle, 
				{id: row.id_rel}, 
				apoc.map.removeKeys(row, ['id_source', 'id', 'id_rel']), 
				b, 
				apoc.map.removeKeys(row, ['id_source', 'id', 'id_rel'])
			) 
			YIELD rel 
			RETURN rel
			"""
	else:
		pass
	if query is not None:
		gu.execute_query(logger, ctx, championship, None, query, batch=batch)


def delete_game_events(logger, ctx, championship, list_games):
	"""
	Function to delete game events.
	"""
	start_time = time.time()
	query = """
		CALL apoc.periodic.iterate('
			MATCH (game:Game WHERE game.gid IN $list_games)<-[:OCCURS_IN]-(event) 
			RETURN event
			', '
			DETACH DELETE event
			', {batchSize: 100, parallel: false, params: {list_games: $list_games}})
		"""
	gu.execute_query(logger, ctx, championship, None, query, list_games=list_games)
	logger.info("%s :: %s :: DELETE_GAME_EVENTS :: %s", os.path.basename(__file__), os.getpid(), util.get_duration(start_time))


def link_consecutive_game_events(logger, ctx, championship, list_games):
	"""
	Function to link consecutive game events.
	"""
	start_time = time.time()
	query = """
		CALL apoc.periodic.iterate('
			MATCH (game:Game WHERE game.gid IN $list_games) 
			RETURN game
			', '
			WITH game 
			CALL (game) { 
				MATCH (game)<-[:OCCURS_IN]-(event:Event) 
				WITH event 
				ORDER BY event.sec ASC 
				WITH collect(event) AS events 
				FOREACH (n IN range(0, SIZE(events)-2) | 
					FOREACH (prec IN [events[n]] | 
						FOREACH (next IN [events[n+1]] | MERGE (prec)-[:NEXT]->(next)))) 
			}
			', {batchSize: 100, parallel: false, params: {list_games: $list_games}})
		"""
	gu.execute_query(logger, ctx, championship, None, query, list_games=list_games)
	logger.info("%s :: %s :: LINK_CONSECUTIVE_GAME_EVENTS :: %s", os.path.basename(__file__), os.getpid(), util.get_duration(start_time))


def set_event_information(logger, ctx, championship, list_games):
	"""
	Function to calculate event information.
	"""
	start_time = time.time()
	query = """
		CALL apoc.periodic.iterate('
			MATCH (homeTeam)-[:BOXSCORE]->(game:Game 
				WHERE game.gid =~ \"(?i)[0-9]{9}\"+homeTeam.shn 
				AND game.gid IN $list_games
			)<-[:BOXSCORE]-(visitorTeam) 
			CALL (homeTeam, game, visitorTeam) { 
				MATCH (game)<-[r1:PLAYS|BOXSCORE]-()-[action]->(event)-[:OCCURS_IN]->(game) 
				WITH 
					event, 
					CASE type(action) WHEN \"TWO_PT_MADE\" THEN 2 WHEN \"THREE_PT_MADE\" THEN 3 WHEN \"FT_MADE\" THEN 1 ELSE 0 END AS points, 
					CASE WHEN r1.tid = homeTeam.tid THEN true ELSE false END AS is_home 
				ORDER BY event.sec 
				WITH collect({event: event, points: points, is_home: is_home}) AS events 
				UNWIND range(0, size(events)-1) AS i 
				WITH 
					i, 
					events[i].event AS event, 
					reduce(acc = 0, j IN range(0, i) | CASE WHEN events[j].is_home = true THEN acc+events[j].points ELSE acc END) AS homeScore, 
					reduce(acc = 0, j IN range(0, i) | CASE WHEN events[j].is_home = false THEN acc+events[j].points ELSE acc END) AS visitorScore 
				WITH 
					event, 
					max(homeScore) AS homeScore, 
					max(visitorScore) AS visitorScore 
				RETURN 
					event, 
					homeScore, 
					visitorScore, 
					abs(homeScore-visitorScore) AS spread 
			} 
			RETURN event, homeScore, visitorScore, spread
			', '
			SET event += {hscr: homeScore, vscr: visitorScore, sprd: spread}
			', {batchSize: 50, parallel: false, params: {list_games: $list_games}})
			"""
	gu.execute_query(logger, ctx, championship, None, query, list_games=list_games)
	logger.info("%s :: %s :: SET_EVENT_INFORMATION :: %s", os.path.basename(__file__), os.getpid(), util.get_duration(start_time))


def link_consecutive_playoff_games(logger, ctx, championship, season):
	"""
	Function to link consecutive playoff games.
	"""
	start_time = time.time()
	query = """
		CALL apoc.periodic.iterate('
			MATCH (:Season {season: $season})<-[:BELONGS_TO]-(game_a:Game WHERE game_a.number = 1)<-[:BOXSCORE]-(team:Team) 
			RETURN game_a, collect(team) AS teams
			', '
			MATCH (game_b:Game) 
			WHERE all(team IN teams WHERE exists((game_b)<-[:BOXSCORE]-(team))) 
			AND game_a.dat < game_b.dat 
			WITH game_a, game_b 
			ORDER BY game_b.dat ASC 
			WITH game_a, collect(game_b) AS games 
			WITH game_a + games AS games 
			FOREACH (n IN range(0, size(games)-2) | 
				FOREACH (prec IN [games[n]] | 
					FOREACH (next IN [games[n+1]] | MERGE (prec)-[:NEXT]->(next))))
			', {batchSize: 100, parallel: false, params: {season: $season}})
		"""
	gu.execute_query(logger, ctx, championship, None, query, season=season)
	logger.info("%s :: %s :: LINK_CONSECUTIVE_PLAYOFF_GAMES :: %s", os.path.basename(__file__), os.getpid(), util.get_duration(start_time))


def set_season_playoff_dates(logger, ctx, championship, season):
	"""
	Function to set season playoff date.
	"""
	start_time = time.time()
	query = """
		MATCH (season:Season {season: $season}) 
		CALL (season) { 
			MATCH (season)<-[:BELONGS_TO]-(game:Game WHERE game.type =~ '(?i)playoff.*') 
			RETURN game.dat AS date 
			ORDER BY date ASC LIMIT 1 
			UNION ALL 
			MATCH (season)<-[:BELONGS_TO]-(game:Game WHERE game.type =~ '(?i)playoff.*') 
			RETURN game.dat AS date 
			ORDER BY date DESC LIMIT 1 
		} 
		WITH season, collect(date) AS dates 
		SET season.start_playoff = dates[0], season.end_playoff = dates[1]
		"""
	gu.execute_query(logger, ctx, championship, None, query, season=int(season))
	logger.info("%s :: %s :: SET_SEASON_PLAYOFF_DATES :: %s", os.path.basename(__file__), os.getpid(), util.get_duration(start_time))


def set_game_description(logger, ctx, championship, list_games):
	"""
	Function to set game description.
	"""
	start_time = time.time()
	query = """
		CALL apoc.periodic.iterate('
			MATCH (home_team)-[:BOXSCORE]->(game:Game 
				WHERE game.gid IN $list_games 
				AND game.gid =~ "(?i)[0-9]{9}"+home_team.shn 
			)<-[:BOXSCORE]-(visitor_team) 
			RETURN 
				game, 
				visitor_team.nik + " - " + home_team.nik + " - " + apoc.date.format(datetime(toString(game.dat)).epochMillis, "ms", "EEEE, d MMMM y") AS description 
			', '
			SET game.description = description
			', {batchSize: 1000, parallel: true, params: {list_games: $list_games}})
		"""
	gu.execute_query(logger, ctx, championship, None, query, list_games=list_games)
	logger.info("%s :: %s :: SET_GAME_DESCRIPTION :: %s", os.path.basename(__file__), os.getpid(), util.get_duration(start_time))
