from abstract_classes import Unit

class Arena:
    def __init__(self):
        self._entities = {} #troops: [], towers: [], spells: [], attacks: [], in no particular order

    def get_entity_type(self, entity: Unit) -> str:
        if entity.TYPE == "unit":
            return entity.SUBTYPE
        return entity.TYPE

    def remove_entity(self, entity: Unit) -> None:
        entity_type = self.get_entity_type(entity)
        if entity_type in self._entities:
            self._entities[entity_type].remove(entity)

    def add_entity(self, entity: Unit) -> None:
        entity_type = self.get_entity_type(entity)
        if entity_type not in self._entities:
            self._entities[entity_type] = []
        self._entities[entity_type].append(entity)

    def get_entities_by_type(self, entity_types: list):
        return [entity for entity_type in entity_types for entity in self._entities.get(entity_type, [])]

    def get_entities_raw(self):
        return self._entities

    def get_all_entities(self): #all entities
        return [x for vals in self._entities.values() for x in vals]

    def tick(self):
        pass

    def cleanup(self):
        pass