from infoblox.test.ibtest import IBTestCase

import infoblox.one.onedb as onedb
import uuid
import random as rand
import infoblox.one.base as bs
from infoblox.dns.dnstypes import (Member_Server, Custom_Router,
                                      Custom_DNS_Server, Custom_Option)
from infoblox.dns.dhcptypes import (Email_Address, Common_Dhcp_Props,
                                    Bootp_Props, Zone_Association,
                                    Ms_Dhcp_Server)

import infoblox.one.util as ut
# some of init members are generated, but some of them are static
# !!!! better solution - ONLY one call to set static
class AutoTest(IBTestCase):


    # to initialize substructs at first time
    substr_created = False
    def setUpSuite(self):
        pass

    def setUp(self):
        pass

    def init_members(self):
        self.common_member_hooks = {
            'range_high_water_mark': rand.randint(70, 99),
            'range_low_water_mark':  rand.randint(0, 29),
            'range_low_water_mark_reset': rand.randint(30, 50),
            'range_high_water_mark_reset': rand.randint(51, 69),
        }
        self.common_skipped = (
            'gog_revision',
            )
        #for substruct use
        self.mapped_sub_dict = {
                'member_dhcp': 'grid_member',
                }

        self.db = onedb.Db()

    def tearDownSuite(self):
        pass

    def _gen_class (self):

        self.init_members()
        if AutoTest.substr_created == False:
            self._gen_members()
            firs_obj = self.class_name(self.db, self.keys_to_assign)
            AutoTest.substr_created = True

        self._gen_members()

        obj = self.class_name(self.db, self.keys_to_assign)

        return obj

    def has_attr_elems(self, key, member_list):
        for attribute in member_list[key]:
            if attribute == 'elements':
                return True
        return False

    def _gen_members(self, spec_hooks={}):
        member_list = self.class_name.members
        # variable for saving members, we are going to set (with all attributes)
        self.values = {}

        # dict of generated values
        self.keys_to_assign = {}
        syntaxes = 'None'
        for key in member_list:

            if not key.startswith('_'):
                if key in self.common_skipped or\
                        key in self.memb_skipped:
                    continue
                # check hooks
                if key in self.member_hooks:
                    self.keys_to_assign[key] =\
                            self.member_hooks[key]
                    self.values[key] = member_list[key]
                    continue
                elif key in spec_hooks:
                    self.keys_to_assign[key]=\
                            spec_hooks[key]
                    self.values[key] = member_list[key]
                    continue

                #check substructs
                if key in self.class_name._substructs:
                    if self.class_name._substructs[key].dbtype\
                        in self.substr_skip:
                            continue

                    self.keys_to_assign[key] = self._gen_substruct_list(
                                self.class_name._substructs[key].objectclass)
                    self.values[key] = member_list[key]
                    continue

                # add that to skip_vars!!!!!
                # they dont have syntaxes attribute and some of them
                # are a wrapper for substructs
                # others after inserting into the
                # db may change(dhcp_utilization_status)
                # for test !!!!!! skip all nested elems
                # check fields with elems attribute
                if self.has_attr_elems(key, member_list) == True:
                    if member_list[key]['class'] != None and\
                    type(member_list[key]['class']) != tuple:
                        self.keys_to_assign[key] = \
                            self._gen_substruct_list(
                                member_list[key]['class'])[0]
                    else:
                        self.keys_to_assign[key] = \
                                self._gen_obj_values(
                                        key,
                                        member_list[key]['type'],
                                        values\
                                        =member_list[key]['values'])
                    self.values[key] = member_list[key]
                    continue

                self.values[key] = member_list[key]

                if member_list[key]['syntaxes'] != None:
                    syntaxes = member_list[key]['syntaxes'][0]

                #check if uuid or not
                if member_list[key]['uuid'] == True:
                    self.keys_to_assign[key] = uuid.uuid4().hex
                    continue

                self._gen_obj_values(
                        key,
                        member_list[key]['type'],
                        syntaxes)

                syntaxes = 'None'

        return self.keys_to_assign


    def _gen_obj_values(self, key, typ, syntaxes='None', values=()):
        if key in self.member_hooks:
            value_hook = self.member_hooks[key]
            self.keys_to_assign[key] = value_hook
        elif key in self.common_member_hooks:
            value_hook = self.common_member_hooks[key]
            self.keys_to_assign[key] = value_hook
        else:
            self.keys_to_assign[key] = self.gen_value(
                    typ,
                    syntaxes,
                    values=values)
        return self.keys_to_assign[key]



    def _gen_substruct_list(self, object_class):

        some_addresses = [self.gen_net_addr_cidr(8)[0] for i in range(0,3)]
        if object_class == Custom_Option:
            return [
                bs.SubStruct(space='DHCP',
                    name='subnet-mask',
                    value=some_addresses[0])
                ]
        elif object_class == Bootp_Props:
            return [
                Bootp_Props(use_boot_file=True,
                    boot_file="file%d" % i,
                    use_boot_server=True,
                    boot_server="10.0.0.%d" % i,
                    use_next_server=True,
                    next_server="10.0.0.%d" % int(i+1),
                    use_deny_bootp=True,
                    deny_bootp=True)
                for i in range(9,11)
                ]

        elif object_class == Custom_DNS_Server:
            return [
             Custom_DNS_Server(address=s_address)
                     for s_address in some_addresses
            ]

        elif object_class == Email_Address:
            return [
                Email_Address(email_address='info@test.com')
            ]

        elif object_class == Member_Server:
            return [
                Member_Server(
                    grid_member=self.db.ref({'__key':'0'}, 'one.virtual_node'))
                ]


        else:
            print "Skipped substr %s" % object_class
            return None



    def test_insert(self):

        print '\n\ntest_insert'
        obj = self._gen_class()


        with self.db.begin(onedb.RW) as txn:
            obj.insert()

            self._check_read([obj])

            obj.delete()
            txn.abort()

    # returns a list of object keys
    def _get_all_keys(self):
        all_keys = []
        for key in self.values:
            for option in self.values[key]:
                if option == 'key' and self.values[key][option] == True:
                    all_keys.append(key)
        return all_keys


    def test_update(self):

        print '\n\ntest_update'

        obj = self._gen_class()

        all_keys = self._get_all_keys()

        with self.db.begin(onedb.RW) as txn:
            obj.insert()

            # gen values in self.keys_to_assign
            self._gen_members()
            # some fields can be only set in transaction block

            for key in self.values:
                if key not in all_keys:
                    obj[key] = self.keys_to_assign[key]


            obj.update()
            self._check_read([obj])

            obj.delete()
            txn.abort()


    def test_delete(self):

        print '\n\ntest_delete'


        obj = self._gen_class()
        obj_del = self._gen_class()

        with self.db.begin(onedb.RW) as txn:
            obj_del.insert()
            obj.insert()

            obj_del.delete()

            reader = self.class_name_cmd(self.db)

            obj_list = []
            for read_obj in reader.read():
                obj_list.append(read_obj)

            self.assertEqual(len(obj_list), 1)

            for key in self.keys_to_assign:
                if key in self.class_name._substructs:
                    new_name = self._check_substr_nested(key)
                    if new_name == None:
                        self._check_substr(key,
                                obj[key],
                                obj_list[0][key])
                    else:
                        self._check_substr(key,
                                obj[new_name][key],
                                obj_list[0][new_name][key])
                    continue

                self.assertEqual(obj_list[0][key], obj[key])

            obj.delete()

            self.assertRaises(onedb.DBNotFoundError, obj.delete)
            txn.abort()

    def test_read(self):
        print '\n\n test read'
        objs = [self._gen_class() for x in range(0, 3)]

        with self.db.begin(onedb.RW) as txn:
            for obj in objs:
                obj.insert()


            all_keys = self._get_all_keys()
            keyword = all_keys[0]
            searchfields = {
                    keyword:{
                'value': objs[0][keyword],
                'search_type': 'EXACT' }}


            self._check_read([objs[0]], sf=searchfields)

            # search on comment field ? is this in all classes ?
            # check fields with sorting
            for key in self.search_fields:
                sort_objs = []
                check_field = objs[0][key].split(
                        self.search_fields[key])[0]
                searchfields = dict(
                        {key:{
                    'value': check_field,
                    'search_type': 'REGEX' }})
                sortfields = [{
                    'field': keyword,
                    'sort_type': 'ASC' }]
                # very syntatic !!!

                for obj in objs:
                    if obj[key].startswith(check_field):
                        sort_objs.append(obj)
                if self.has_attr_elems(
                        keyword,
                        self.class_name.members,
                                    ) == False and\
                     ( self.values[keyword]['syntaxes'][0] != 'ipv4_addr' or\
                       self.values[keyword]['syntaxes'][0] != 'ip_addr' or\
                       self.values[keyword]['syntaxes'][0] != 'ipv6_addr' ):
                    deco = [
                    ((ut.dotted_quad_to_num(a[keyword])),a) for a in sort_objs]

                else:
                    deco = [( (a[keyword]),a ) for a in sort_objs]

                deco.sort()
                sorted_objs = [obj for key, obj in deco]
                print sorted_objs

                self._check_read(sorted_objs,
                        sf=searchfields,
                        sortf=sortfields)
            txn.abort()



    #all checks are performed in tansaction block
    #special check if the substruct is get by other substruct-
    #self.substr_check - dict with tuple values
    def _check_substr_nested(self, substr_name):
        for key in self.substr_check:
            if substr_name in self.substr_check[key]:
                return key
        return None

    # ! objs - must be a list with one or more objects
    # multiple ojects are checked if we have parameters as
    # sortfield or (and) searchfield all founded readed objects
    # must be in the same order as objs
    def _check_read(self,
            objs, sf={}, sortf=[]):

        reader = self.class_name_cmd(self.db)

        def check_class(read_obj, obj):
            for key in self.keys_to_assign:
                if key in self.class_name._substructs:
                    new_name = self._check_substr_nested(key)
                    if new_name == None:
                        self._check_substr(key, obj[key], read_obj[key])
                    else:
                        self._check_substr(key, obj[new_name][key],
                                read_obj[new_name][key])
                    continue
                #print key, read_obj[key], obj[key], self.values[key]['type']
                self.assertEqual(read_obj[key], obj[key])

        print sf, sortf
        n = 0
        for read_obj in reader.read(searchfields=sf,
                sortfields=sortf):
            print n
            #if len(sf) != 0 and len(sortf) != 0:
            #    print read_obj, '\n\n', objs[n]
            check_class(read_obj,objs[n])
            n += 1



    def _check_substr(self, substr_name, obj_substr, read_obj_substr):
        members = self.db.members(self.class_name._substructs[
            substr_name].dbtype)
        for index in range(0, len(read_obj_substr)):
            for key in members:
                if key in self.skip_substr_field:
                    continue
                if key not in self.mapped_sub_dict:
                    if members[key]['type'] != 'ref'\
                            and not key.startswith('_'):
                        self.assertEqual(read_obj_substr[index][key],
                                obj_substr[index][key])
                else:
                    #print key, self.mapped_sub_dict[key]

                    self.assertEqual(read_obj_substr[index][
                        self.mapped_sub_dict[key]],
                        obj_substr[index][self.mapped_sub_dict[key]])


    def get_default_network_view(self):
        with self.db.begin(onedb.RO):
            return self.db.call('?dns.network_view', {
                'name': 'default'}, single=True).ref()


    # use form one/util.py dotted_quad_to_num and others
    def gen_router_addr(self, net_addr, cidr):
        net_addr_int = ut.dotted_quad_to_num(net_addr)

        router_addr = rand.randrange(net_addr_int + 1,
                net_addr_int | (1 << (2**5 - cidr) - 2))

        return ut.num_to_dotted_quad(router_addr)

    def gen_broadcast_addr(self, net_addr, cidr):
        net_addr_int = ut.dotted_quad_to_num(net_addr)
        reverse_mask = ~ut.dotted_quad_to_num(ut.cidr_to_mask(cidr))
        broad_addr = ut.num_to_dotted_quad(net_addr_int | reverse_mask)
        print net_addr, ut.num_to_dotted_quad(reverse_mask), broad_addr
        return broad_addr

    def gen_net_addr_cidr(self, some_cidr=None):
        if some_cidr == None:
            cidr = rand.choice( (8, 16, 24) )
            #cidr = rand.randrange(8, 2**5 - 2)
        else:
            if 8 > some_cidr or some_cidr > 2**5 - 2:
                return None, None
            cidr = some_cidr

        ip = rand.randrange(1, 2**cidr)
        ip_addr = ut.num_to_dotted_quad(ip << (2**5 - cidr))
        return ip_addr, cidr


# just one function to generate values of type we need

    def gen_value(self, typ, syntaxes, values=()):
        cidr = 24
        if syntaxes == 'None':
            if typ == 'uint':
                # ??? Better way ???
                uint_numb = rand.randint(0, 256)
                return uint_numb
            if typ == 'enum':
                return rand.choice(values)
            if typ == 'str':
                return "Here is the default string"
            if typ == 'bool':
                return True
        else:
            if syntaxes == 'text':
                return 'Here is the default string'
            if syntaxes == 'ipv4_addr' or syntaxes == 'ip_addr':
                return self.gen_net_addr_cidr(cidr)[0]
            if syntaxes == 'unsigned_int':
                return rand.randint(0, 256)
            if syntaxes == 'mask':
                return cidr
            if syntaxes == 'ci_string_list':
                return True
            if syntaxes == 'signed_int':
                # that numbers are set for lease_time, starting with
                # 86400 s
                return rand.randint(86400, 47472000)
            if syntaxes == 'dns_name':
                return 'info.com'
            if syntaxes == 'email_address':
                return 'def@info.com'
