'''

New Integration Test for expunging KVM VM.

@author: Youyk
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.config_operations as conf_ops
import time
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Test storage capacity when using expunge vm')
    if conf_ops.get_global_config_value('vm', 'deletionPolicy') != 'Delay' :
        test_util.test_skip('vm delete_policy is not Delay, skip test.')
        return

    zone_uuid = res_ops.query_resource(res_ops.ZONE)[0].uuid
    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('status', '=', 'Connected', cond)
    host = res_ops.query_resource_with_num(res_ops.HOST, cond, limit = 1)
    if not host:
        test_util.test_skip('No Enabled/Connected host was found, skip test.' )
        return True

    ps = res_ops.query_resource_with_num(res_ops.PRIMARY_STORAGE, cond, limit = 1)
    if not ps:
        test_util.test_skip('No Enabled/Connected primary storage was found, skip test.' )
        return True

    host = host[0]
    ps = ps[0]

    host_res = vol_ops.get_local_storage_capacity(host.uuid, ps.uuid)[0]
    avail_cap = host_res.availableCapacity

    vm = test_stub.create_vm(vm_name = 'basic-test-vm', host_uuid = host.uuid)
    test_obj_dict.add_vm(vm)
    time.sleep(1)
    vm.destroy()
    vm.expunge()
    host_res2 = vol_ops.get_local_storage_capacity(host.uuid, ps.uuid)[0]
    avail_cap2 = host_res.availableCapacity
    if avail_cap != avail_cap2:
        test_util.test_fail('PS capacity is not same after create/expunge vm on host: %s. Capacity before create vm: %s, after expunge vm: %s ' % (host.uuid, avail_cap, avail_cap2))
    test_util.test_pass('Expunge VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
