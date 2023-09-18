import os
from dotenv import load_dotenv
import re
from flask import Flask, render_template, request
from pymongo import MongoClient
import subprocess


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.flaskenv'))

mongo_username = os.environ.get('MONGO_USERNAME')
mongo_password = os.environ.get('MONGO_PASSWORD')

# Create an instance of the Flask web application and assign it to the variable 'app'
app = Flask(__name__)

# Connect to MongoDB
cluster= MongoClient(f'mongodb+srv://{mongo_username}:{mongo_password}@cluster0.cxziugw.mongodb.net/?retryWrites=true&w=majority')
db = cluster["Project"]
collection = db["Subtitles"]


# Define a custom filter for converting timestamp to seconds
@app.template_filter('timestamp_to_seconds')
def timestamp_to_seconds(timestamp):
    parts = timestamp.split(':')
    minutes = int(parts[0])
    seconds = int(parts[1])
    total_seconds = minutes * 60 + seconds
    return total_seconds




@app.route('/', methods=['GET', 'POST'])
def search_results(search_term=None):
    if request.method == 'POST':
        search_term = request.form.get('search_term')
        search_terms = search_term.split()
        consecutive_pairs = ["{} {}".format(search_terms[i], search_terms[i + 1]) for i in range(len(search_terms) - 1)]
        all_search_terms = search_terms + consecutive_pairs   # Split the input into individual words
        regex_pattern = "|".join([r'\b{}\b'.format(re.escape(term)) for term in all_search_terms])

        if search_term:

            
            pipeline = [
                {
                    "$match": {
                        "$or": [
                            {
                                "keywords.keyword": {
                                    "$regex": regex_pattern,
                                    "$options": "i"
                                }
                            },
                            {
                                "title": {
                                    "$regex": regex_pattern,
                                    "$options": "i"
                                }
                            }
                        ]
                    }
                },
                {
                    "$unwind": "$keywords"
                },
                {
                    "$match": {
                        "$or": [
                            {
                                "keywords.keyword": {
                                    "$regex": regex_pattern,
                                    "$options": "i"
                                }
                            },
                            {
                                "title": {
                                    "$regex": regex_pattern,
                                    "$options": "i"
                                }
                            }
                        ]
                    }   
                },
                {
                    "$group": {
                        "_id": "$_id",
                        "result": {
                            "$first": {
                                "title": "$title",
                                "thumbnail": "$thumbnail",
                                "url": "$url",
                                "keyword": {
                                    "$cond": {
                                        "if": {
                                            "$regexMatch": {
                                                "input": "$keywords.keyword",
                                                "regex": regex_pattern,
                                                "options": "i"
                                            }
                                        },
                                        "then": "$keywords.keyword",
                                        "else": ""
                                    }
                                },
                                "timestamps": {
                                    "$cond": {
                                        "if": {
                                            "$regexMatch": {
                                                "input": "$keywords.keyword",
                                                "regex": regex_pattern,
                                                "options": "i"
                                            }
                                        },
                                        "then": "$keywords.occurences.timestamp",
                                        "else": []
                                    }
                                },
                                "sentences": {
                                    "$cond": {
                                        "if": {
                                            "$regexMatch": {
                                                "input": "$keywords.keyword",
                                                "regex": regex_pattern,
                                                "options": "i"
                                            }
                                        },
                                        "then": "$keywords.occurences.sentence",
                                        "else": []
                                    }
                                }
                            }
                        }
                    }
                },
                {
                    "$replaceRoot": { "newRoot": "$result" }
                }
            ]
            # Execute the aggregation pipeline
            result = list(collection.aggregate(pipeline))

            # Iterate through the results
            for doc in result:
                #Initialize a variable to count the number of terms from 'all_search_terms' that matched the document.
                doc['matched_terms_count'] = 0  # Initialize the count to 0

                for term in all_search_terms:
                    # Check if the term matches either the 'title' or 'keyword' field of the document
                    if re.search(r'\b{}\b'.format(re.escape(term)), doc['title'], re.I) or ('keyword' in doc and re.search(r'\b{}\b'.format(re.escape(term)), doc['keyword'], re.I)):
                        doc['matched_terms_count'] += 1  # Increment count if a term matches 'title' or 'keyword'
            
            # Sort the results by matched_terms_count in descending order
            result.sort(key=lambda x: x['matched_terms_count'], reverse=True)
        else: 
            error_message = "Please enter a non-empty value in the search box."
            return render_template('search_form.html', result=[], search_term=search_term, error_message=error_message)

        
        if not result:
            no_results_message = f"There are no videos related to '{search_term}'."
            return render_template('search_result.html', result=[], search_term=search_term, no_results_message=no_results_message)


        return render_template('search_result.html', result=result, search_term=search_term)

    return render_template('search_form.html', result=[], search_term = None)   # Render a search form initially


if __name__ == "__main__":
    app.run()