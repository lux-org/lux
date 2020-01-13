import pandas as pd
import json
class Dataset:
	def __init__(self,filename="",df="", schema=[]):
		self.filename = filename
		if (self.filename!=""):
			self.df = self.loadCSV()
		else:
			self.df = df
		
		self.schema = schema
		# self.df_json  = self.df.to_json(orient='records')
		self.computeDatasetMetadata()
	def computeDatasetMetadata(self):
		self.attrList = list(self.df.columns)
		self.dataTypeLookup = {}
		self.dataType = {}
		self.computeDataType()
		self.dataModelLookup = {}
		self.dataModel = {}
		self.computeDataModel()
		self.computeStats()
	def set_df(self,df):
		self.df = df 
		self.computeDatasetMetadata() 
	def __repr__(self):
		return f"<Dataset Obj: {str(self.filename)}>"

	def loadCSV(self):
		df = pd.read_csv(self.filename)
		return df

	def computeDataType(self):
		# df = self.df
		# self.dataType = {
		# 	"quantitative":list(dfw.dtypes[df.dtypes=="float64"].keys()) + list(df.dtypes[df.dtypes=="int64"].keys()),
		# 	"categorical":list(df.dtypes[df.dtypes=="object"].keys()),
		# 	"ordinal": [],
		# 	"date":[]
		# }

		for attr in self.attrList:
			if self.df.dtypes[attr]=="float64" or self.df.dtypes[attr]=="int64":
				if cardinality(self.df,attr)<10:
					self.dataTypeLookup[attr]="categorical"
				else:
					self.dataTypeLookup[attr]="quantitative"
			elif self.df.dtypes[attr]=="object":
				self.dataTypeLookup[attr]="categorical"
		# Override with schema specified types
		for attrInfo in self.schema:
			key= list(attrInfo.keys())[0]
			if ("dataType" in attrInfo[key]):
				self.dataTypeLookup[key]= attrInfo[key]["dataType"]
		# for attr in list(df.dtypes[df.dtypes=="int64"].keys()):
		# 	if self.cardinality[attr]>50:
		self.dataType = self.mapping(self.dataTypeLookup)

	def computeDataModel(self):
		# TODO: Need to be modified to take in schema for overriding defaults
		self.dataModel = {
			"measure":self.dataType["quantitative"],
			"dimension":self.dataType["ordinal"]+self.dataType["categorical"]+self.dataType["date"]
		}
		# Override with schema specified types
		for attrInfo in self.schema:
			key= list(attrInfo.keys())[0]
			if ("dataModel" in attrInfo[key]):
				dataModel = attrInfo[key]["dataModel"]
				if (dataModel=="measure"):
					self.dataModel["dimension"].remove(key)
					self.dataModel["measure"].append(key)
				else:
					self.dataModel["measure"].remove(key)
					self.dataModel["dimension"].append(key)

		

		self.dataModelLookup = self.reverseMapping(self.dataModel)

	def mapping(self,rmap):
	    groupMap = {}
	    uniqueVal = list(set(rmap.values()))
	    for val in ["quantitative","ordinal","categorical","date"]:
	        groupMap[val] = list(filter(lambda x:rmap[x]==val,rmap))
	    return groupMap

	def reverseMapping (self, map):
		reverseMap ={}
		for valKey in map:
			for val in map[valKey]:
				reverseMap[val]=valKey
		return reverseMap

	def computeStats(self):
		# precompute statistics
		self.cardinality = {}
		for dimension in self.df.columns:
			self.cardinality[dimension]=cardinality(self.df,dimension)
		
def cardinality(df,columnName):
	return len(df[columnName].unique())