
import flask
from xml_sitemap_generator.job import main
from jinja2 import Template

##### **** APPLICATION **** #####

app = flask.Flask(__name__)


@app.route('/')
def index():
    # html with link to /load page
    
    return flask.render_template('index.html')


@app.route('/load', methods=['GET', 'POST'])
def load_data_to_database_csv():
  url = '/load'
  html = f"""
  <form action="{url}" method="post" enctype="multipart/form-data">
    <input type="file" name="file">
    <input type="submit" value="Upload">
  </form>
  """
  
  # if request is GET then load html
  if flask.request.method == 'GET':
    return html
  
  # if  request is POST then load data to database
  if flask.request.method == 'POST':
    
    file = flask.request.files['file']
    
    list_of_filenames = main(file)
    
    print(list_of_filenames)
    
    # list_of_filenames to html template 
    html = Template('''
        <ul>        
            {% for filename in list_of_filenames %}
                <li>
                    <span>{{ filename }}</span>
                </li>
            {% endfor %}
        </ul>
    ''')
    
    return html.render(list_of_filenames = list_of_filenames)

if __name__ == "__main__":
    app.run(debug=True)