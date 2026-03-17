class ExampleService:
    def __init__(self):
        # Simulación de base de datos en memoria
        self.data = [
            {'id': 1, 'name': 'Ejemplo 1', 'description': 'Descripción del ejemplo 1'},
            {'id': 2, 'name': 'Ejemplo 2', 'description': 'Descripción del ejemplo 2'}
        ]
        self.next_id = 3
    
    def get_all(self):
        return self.data
    
    def get_by_id(self, id):
        return next((item for item in self.data if item['id'] == id), None)
    
    def create(self, data):
        new_item = {
            'id': self.next_id,
            'name': data.get('name'),
            'description': data.get('description')
        }
        self.data.append(new_item)
        self.next_id += 1
        return new_item
    
    def update(self, id, data):
        item = self.get_by_id(id)
        if item:
            item['name'] = data.get('name', item['name'])
            item['description'] = data.get('description', item['description'])
            return item
        return None
    
    def delete(self, id):
        item = self.get_by_id(id)
        if item:
            self.data.remove(item)
            return True
        return False