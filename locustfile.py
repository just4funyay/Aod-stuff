from locust import HttpUser, task

class HelloWorldUser(HttpUser):
    weight = 5
    @task
    def testing(self):
        self.client.get('/api1/get-data-aod/')
        #self.cleint.get('/world')