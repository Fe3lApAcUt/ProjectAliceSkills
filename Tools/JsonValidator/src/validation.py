import json
from collections import defaultdict
from pathlib import Path

from abc import ABC, abstractmethod
from jsonschema import Draft7Validator, exceptions


class validation(ABC):
	def __init__(self, modulePath: Path):
		self.modulePath = modulePath
		self.validModule = self.infinidict()
		self.dir_path = Path(__file__).resolve().parent
		self.base_path = self.dir_path.parent.parent.parent
		self.error = 0

	def infinidict(self):
		return defaultdict(self.infinidict)

	@property
	def validModules(self) -> dict:
		return self.validModule
	
	@property
	@abstractmethod
	def JsonSchema(self) -> dict:
		pass
	
	@property
	@abstractmethod
	def JsonFiles(self) -> list:
		pass

	@property
	def moduleName(self) -> str:
		return self.modulePath.name

	@property
	def moduleAuthor(self) -> str:
		return self.modulePath.parent.name

	def validateSyntax(self, file: Path) -> dict:
		data = dict()
		try:
			data = json.loads(file.read_text())
		except ValueError as e:
			self.validModule['syntax'][file.name] = str(e)
			self.error = 1
		return data

	def validateSchema(self) -> None:
		schema = self.JsonSchema
		for file in self.JsonFiles:
			self.validModule['schema'][file.name] = list()
			jsonPath = self.validModule['schema'][file.name]
			# try to load json from file and return error when the format is invalid
			data = self.validateSyntax(file)
			
			# validate the loaded json
			try:
				Draft7Validator(schema).validate(data)
			except exceptions.ValidationError:
				self.error = 1
				for error in sorted(Draft7Validator(schema).iter_errors(data), key=str):
					jsonPath.append(error.message)

	@abstractmethod
	def validate(self) -> bool:
		pass