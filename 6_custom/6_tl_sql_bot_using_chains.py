from operator import itemgetter

from dotenv import load_dotenv
from langchain.chains.sql_database.query import create_sql_query_chain
from langchain_anthropic import ChatAnthropic
from langchain_community.tools import QuerySQLDataBaseTool
from langchain_community.utilities import SQLDatabase

import re

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.tracers import ConsoleCallbackHandler

# Load environment variables from .env
load_dotenv()

# Instead of writing this method, can add a Runnable in the chain to make the llm extract the sql from the text
# It can also verify for errors during that
def extract_sql(text):
  """Extracts SQL code from a given text string.

  Args:
    text: The input text string.

  Returns:
    The extracted SQL code, or None if no SQL code is found.
  """

  # Regular expression to match SQL code enclosed in triple backticks
  pattern = r"```sql(.*?)```"
  pattern = re.escape(pattern)

  match = re.search(pattern, text)

  if match:
    return match.group(1)
  else:
    return None

# connect to the database
mysql_uri = 'mysql+mysqlconnector://root:test@localhost:49794/test'
#  db name is test which is running on docker (Deals-API)

db = SQLDatabase.from_uri(mysql_uri)
print(db.dialect)
print(db.get_usable_table_names())
print(db.get_table_info())


llm = ChatAnthropic(
    model="claude-3-5-sonnet-20240620",
    temperature=0,
    max_tokens=1024,
    timeout=None,
    max_retries=2,
    # other params...
)

execute_query = QuerySQLDataBaseTool(db=db)
write_query = create_sql_query_chain(llm, db)
# sanitize the output, which comes in below format
# To find out how many deals are activated, we need to look at the `ttd_deal` table and count the number of deals with the `proposal_state` of 'Activated'. Here's the query:
#
# ```sql
# SELECT COUNT(*) AS activated_deals
# FROM `ttd_deal`
# WHERE `proposal_state` = 'Activated' AND `deleted` = 0;
# ```]
sanitize_output = RunnableLambda(lambda x: extract_sql(x))

answer_prompt = PromptTemplate.from_template(
    """Given the following user question, corresponding SQL query, and SQL result, answer the user question.

Question: {question}
SQL Query: {query}
SQL Result: {result}
Answer: 

Make sure the answer is a user friendly text"""
)

chain = (
    RunnablePassthrough.assign(query=write_query).assign(
        result=itemgetter("query") | execute_query
    )
    | answer_prompt
    | llm
    | StrOutputParser()
)

# ConsoleCallbackHandler helps us print output of every step of the chain to console
response = chain.invoke({"question": "How many deals are activated. Only return the SQL without any other text or explanation"}, config={'callbacks': [ConsoleCallbackHandler()]})
print(response)

