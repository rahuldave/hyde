#!/usr/bin/env python
import os
import sys
import threading

from optparse import OptionParser
from hydeengine import Generator, Initializer, Server

#import cProfile

PROG_ROOT = os.path.dirname(os.path.abspath( __file__ ))

def main(argv):
    
    parser = OptionParser(usage="%prog [-f] [-q]", version="%prog 0.3b")
    parser.add_option("-s", "--sitepath", 
                        dest = "site_path", 
                        help = "Change the path of the site folder.")
    parser.add_option("-i", "--init", action = 'store_true', 
                        dest = "init", default = False, 
                        help = "Create a new hyde site.")
    parser.add_option("-f", "--force", action = 'store_true', 
                        dest = "force_init", default = False, help = "")
    parser.add_option("-t", "--template", 
                        dest = "template", 
                        help = "Choose which template you want to use.")
    parser.add_option("-g", "--generate", action = "store_true",
                        dest = "generate", default = False, 
                        help = "Generate the source for your hyde site.")
    parser.add_option("-k", "--keep_watching", action = "store_true",
                        dest = "keep_watching", default = False,
                        help = "Start monitoring the source folder for changes.")                    
    parser.add_option("-d", "--deploy_to", 
                        dest = "deploy_to", 
                        help = "Change the path of the deploy folder.")
    parser.add_option("-w", "--webserve", action = "store_true",
                        dest = "webserve", default = False, 
                        help = "Start an instance of the CherryPy webserver.")

    (options, args) = parser.parse_args()
    
    if len(args):
        parser.error("Unexpected arguments encountered.")
        
    if not options.site_path:
        options.site_path = os.getcwdu()

    if options.deploy_to:
        options.deploy_to = os.path.abspath(options.deploy_to)
    
    if options.init:
        initializer = Initializer(options.site_path)
        initializer.initialize(PROG_ROOT,
                        options.template, options.force_init)

    generator = None
    server = None         
               
    def quit(*args, **kwargs):
        if server and server.alive:
            server.quit()
        if generator:
            generator.quit()
        

    if options.generate:
        generator = Generator(options.site_path)
        generator.generate(options.deploy_to, options.keep_watching, quit)        

    if options.webserve:
        server = Server(options.site_path)
        server.serve(options.deploy_to, quit)
        
    if ((options.generate and options.keep_watching)   
                    or
                    options.webserve):
        try:
            print "Letting the server and/or the generator do their thing..."
            if server:
                server.block()
                if generator:
                    generator.quit()
            elif generator:
                generator.block()
        except:
            print sys.exc_info()
            quit()
    
    if argv == []:
        print parser.format_option_help()
        
    
if __name__ == "__main__":
    main(sys.argv[1:])
    # cProfile.run('main(sys.argv[1:])', filename='hyde.cprof')
    # import pstats
    # stats = pstats.Stats('hyde.cprof')
    # stats.strip_dirs().sort_stats('time').print_stats(20)