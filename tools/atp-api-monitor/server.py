#!/usr/bin/env python3

import test_a2p_api

import tornado.ioloop
import tornado.web

UAT_ENV = 'UAT'
PROD_ENV = 'PROD'
COUNTY = 'tulare'


class ProdHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_status(200)
        prod_response = test_a2p_api.test_fetch_citation(PROD_ENV, COUNTY)
        print('Sending PROD reply...', flush=True)
        self.write('PROD: {}'.format(prod_response.status_code))
        print('Finished sending PROD reply.', flush=True)


class UATHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_status(200)
        uat_response = test_a2p_api.test_fetch_citation(UAT_ENV, COUNTY)
        print('Sending UAT reply...', flush=True)
        self.write('UAT: {}'.format(uat_response.status_code))
        print('Finished sending UAT reply.', flush=True)


def make_app():
    return tornado.web.Application([
        (r"/prod", ProdHandler),
        (r"/uat", UATHandler),
    ])


if __name__ == "__main__":
    port = 80
    app = make_app()
    app.listen(port)
    print('Listening on port {}'.format(port))
    tornado.ioloop.IOLoop.current().start()
