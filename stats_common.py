# Common functions for all stats scripts
import MySQLdb
import cairo
import pycha.line

def db_connection():
	return MySQLdb.connect(host='127.0.0.1', port=3306,
                    user='mail',
                    use_unicode=1, charset='utf8', db='nanogmail')
                    
def generate_chart(dataset, name):
	surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 800, 600)
	options = {"legend" : {"hide" : True}}
	
	chart = pycha.line.LineChart(surface, options)
	chart.addDataset([("ds", dataset)])
	chart.render()
	surface.write_to_png('out/%s.png' % name)
