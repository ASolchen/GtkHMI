import sys
sys.path.insert(0, "..")
import logging
import time
from opcua import Client
from opcua import ua
from backend.managers.connection_classes.base import Connection



class SubHandler(object):

  """
  Subscription Handler. To receive events from server for a subscription
  data_change and event methods are called directly from receiving thread.
  Do not do expensive, slow or network operation there. Create another 
  thread if you need to do such a thing
  """

  def datachange_notification(self, node, val, data):
    print(str(node), val, type(val), type(data.monitored_item.Value.SourceTimestamp), data.monitored_item.Value.SourceTimestamp)



class OPC_Tag_Sub():
  def __init__(self, tag, node, sub, val=None, ts= time.time(), dt="INT"):
    self.tag = tag
    self.node = node
    self.subcription = sub
    self.value = val
    self.timestamp = ts
    self.datatype = dt


class OPCUA_Connection(Connection):
  def __init__(self, connection_manager, idx):
    super().__init__(connection_manager, idx)
    params = self.db_manager.get_rows("OPCUA_ConnectionsParams",["URL", "Pollrate", "AutoConnect"], match_col="ID", match=self.id)[0]
    if not len(params):
      raise KeyError("OPCUA connection parameters missing in project database for ID: {}".format(self.id))
    self.pollrate = params['Pollrate']
    self.url = params['URL']
    self.autoconnect = params['AutoConnect']
    self.tag_subs = {} # use for trackinf tags that are subscibed to

    #logging.basicConfig(level=logging.WARN)
    #logger = logging.getLogger("KeepAlive")
    #logger.setLevel(logging.DEBUG)




    try:
      self.client = Client(self.url)
      # client = Client("opc.tcp://admin@localhost:4840/freeopcua/server/") #connect using a user
      self.client.connect()
      self.client.load_type_definitions()  # load definition of server specific structures/extension objects

      myvar = self.client.get_node("ns=2;s=AB_ETH.PLC.IT_WORKS")
      #obj = root.get_child(["0:Objects", "{}:MyObject".format(idx)])
      #print("myvar is: ", myvar)
      # we can also subscribe to events from server'
      # sub.unsubscribe(handle)
      # sub.delete()
    except: #finally:
      self.client.disconnect()

  def poll(self):
    for tag in self.tag_pool:
      pass

  def read(self, tags: list)->dict:
    results = {}
    for tag in tags:
      if not tag in self.tag_subs:
        sql, params = """SELECT [Tag], [NodeId], [DataType] FROM [Tags] INNER JOIN [OPCUA_TagParams] WHERE Tags.ID = OPCUA_TagParams.ID
AND Tags.ConnectionID = ?;""", [self.id,]
        tag_res = self.db_manager.run_query(sql, args=params)
        if len(tag_res):
          # subscribing to a variable node
          handler = SubHandler()
          sub = self.client.create_subscription(500, handler)
          opc_var = self.client.get_node(tag_res[0]['NodeId'])
          handle = sub.subscribe_data_change(opc_var)
          self.tag_subs[tag] = OPC_Tag(tag, tag_res[0]['NodeId'], sub, dt=tag_res[0]['DataType'])
      else:
        print(f'Need to update {tag}')
    return results


  def write(self, tags):
    pass

  def clear_tag_subs(self):
    pass

