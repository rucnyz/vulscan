    def test_create_host(self):
        self.flags(lock_path=self.tempdir)

        #record
        self.clear_mox()
        self.stubs.Set(hpfcdriver.hpcommon.HP3PARCommon, "get_cpg",
                       self.fake_get_cpg)
        self.stubs.Set(hpfcdriver.hpcommon.HP3PARCommon, "get_domain",
                       self.fake_get_domain)
        _run_ssh = self.mox.CreateMock(hpdriver.hpcommon.HP3PARCommon._run_ssh)
        self.stubs.Set(hpdriver.hpcommon.HP3PARCommon, "_run_ssh", _run_ssh)

        show_host_cmd = 'showhost -verbose fakehost'
        _run_ssh(show_host_cmd, False).AndReturn([pack('no hosts listed'), ''])

        create_host_cmd = ('createhost -persona 1 -domain (\'OpenStack\',) '
                           'fakehost 123456789012345 123456789054321')
        _run_ssh(create_host_cmd, False).AndReturn([CLI_CR, ''])

        _run_ssh(show_host_cmd, False).AndReturn([pack(FC_HOST_RET), ''])
        self.mox.ReplayAll()

        host = self.driver._create_host(self.volume, self.connector)
        self.assertEqual(host['name'], self.FAKE_HOST)