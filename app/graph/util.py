#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
import os
import sys
import pandas as pd


def bolt_to_list(result):
	"""
	Function to transform BOLT result into list of dictionnaries.
	"""
	return [r.data() for r in result]


def bolt_to_df(result):
	"""
	Function to transform BOLT result into DataFrame.
	"""
	return pd.DataFrame(bolt_to_list(result))


def execute_query(logger, ctx, db, result_type, query, **kwargs):
	"""
	Function to execute a Cypher query.
	"""
	result = None
	db = str(db).lower()
	try:
		with ctx.session(database=db) as ses:
			tmp = ses.run(str(query), kwargs)
			if result_type == "df":
				result = bolt_to_df(tmp)
			elif result_type == "single":
				result = tmp.single()
			elif result_type == "list":
				result = bolt_to_list(tmp)
			else:
				pass
	except Exception as e:
		logger.critical("%s :: %s :: EXECUTE_QUERY :: %s :: %s :: %s :: %s :: %s", os.path.basename(__file__), os.getpid(), db, result_type, query, kwargs, e)
	finally:
		return result
