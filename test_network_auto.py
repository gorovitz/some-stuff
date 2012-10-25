import infoblox.test.one.simple_auto_test as sat
import infoblox.dns.network as nw
from infoblox.test.ibtest  import IBTestCase, main
import infoblox.one.onedb as onedb
import infoblox.dns.auth_zone as az
import infoblox.one.base as bs
from infoblox.dns.dnstypes import (Member_Server, Custom_Router,
                                      Custom_DNS_Server, Custom_Option)
from infoblox.dns.dhcptypes import (Email_Address, Common_Dhcp_Props,
                                    Bootp_Props, Zone_Association,
                                    Ms_Dhcp_Server)



class NetworkTest(sat.AutoTest, IBTestCase):


    # number for generating different zones if we need
    zone_numb = 1
    #was done for access in tearDownSuite
    zones = []

    def setUpSuite(self):
        self.db = onedb.Db()


    def setUp(self):
        self.class_name = nw.Network
        self.class_name_cmd = nw.NetworkCmd


    def init_members(self):
        sat.AutoTest.init_members(self)
        (net_addr, cidr) = self.gen_net_addr_cidr()
        # here goes the number of parameters, that should be
        # setted to an object and then refreshed

        some_zone = "test%d.com" % NetworkTest.zone_numb
        NetworkTest.zones.append(az.AuthZone(self.db, {'fqdn': some_zone}))
        with self.db.begin(onedb.RW):
            NetworkTest.zones[-1].insert()

        self.substr_refs = {
                'dns.network_zone_association': NetworkTest.zones[-1].ref()
                }
        NetworkTest.zone_numb += 1



        self.member_hooks = {
            'network_view': self.get_default_network_view(),
            'parent': self.get_default_network_view(),
            'address': net_addr,
            'cidr': cidr,
            'routers': [
                bs.SubStruct(address= self.gen_router_addr(net_addr, cidr))],
            'zone_associations': [Zone_Association(
                zone=NetworkTest.zones[-1].ref(), is_default=False)],
            'access': 'RW',
        }

        #skip some substructs that have no permission to be in one object
        self.substr_skip = (
                'dns.ms_dhcp_member',
                #'dns.option',
                #'dns.router',
                #'dns.network_zone_association',
                #'dns.domain_name_server'
                )
        self.memb_skipped = (
            'apply_template_for_ranges_only',
            'apply_template_for_fixed_addresses_only',
            'parent_name',
            'network_view_name',
            'shared_network_name',
            'auto_create_reversezone',
            'dhcp_utilization_status',
            'contains_address',
            'utilization_update',
            'template',
            'inherited_values',
            'extensible_attributes',
            'common_properties',
            #'bootp_properties',
            )

        #some subsctructs are nested into others
        self.substr_check = {
                'common_properties': ('routers',
                    'domain_name_servers',
                    'options')
                }

        # used in read check
        # key - member to search, value - character to split
        self.search_fields ={
                "comment": ' ',
                "address": '.',
                }


        #could be the same for class_field
        self.skip_substr_field = (
                'position'
                )


    def tearDownSuite(self):
        with self.db.begin(onedb.RW) as txn:
            for x in self.db.cursor('?dns.network'):
                x.delete()
            for zone in NetworkTest.zones:
                zone.delete()

            txn.commit()
        print 'deleted'

if __name__ == '__main__':
    main()


