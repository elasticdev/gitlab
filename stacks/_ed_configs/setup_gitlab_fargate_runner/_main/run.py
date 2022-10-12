class Main(newSchedStack):

    def __init__(self,stackargs):

        newSchedStack.__init__(self,stackargs)


        self.parse.add_optional(key="aws_account_id",default="null")  # probably better to use inputvars

        # Add substack
        self.stack.add_substack('elasticdev:::new_ec2_ssh_key')
        self.stack.add_substack('elasticdev:::aws_iam_role')
        self.stack.add_substack('elasticdev:::ec2_ubuntu_admin')
        self.stack.add_substack('elasticdev:::docker_build_ssh')
        self.stack.add_substack('elasticdev:::delete_resource')

        # Add execgroup
        self.stack.add_execgroup("elasticdev:::gitlab::subgroup")

        self.stack.init_execgroups()
        self.stack.init_substacks()












    def run(self):
    
        self.stack.unset_parallel()
        self.add_job("sshkey")
        self.add_job("iam_role")
        self.add_job("docker_host")
        self.add_job("build")

        return self.finalize_jobs()

    def schedule(self):

        sched = self.new_schedule()
        sched.job = "sshkey"
        sched.archive.timeout = 1200
        sched.archive.timewait = 120
        sched.conditions.retries = 1 
        sched.automation_phase = "infrastructure"
        sched.human_description = "upload user public ssh key"
        sched.on_success = [ "iam_role" ]
        self.add_schedule()

        sched = self.new_schedule()
        sched.job = "iam_role"
        sched.archive.timeout = 1800
        sched.archive.timewait = 120
        sched.automation_phase = "infrastructure"
        sched.human_description = "Create IAM role"
        sched.on_success = [ "docker_host" ]
        self.add_schedule()

        sched = self.new_schedule()
        sched.job = "docker_host"
        sched.archive.timeout = 1800
        sched.archive.timewait = 120
        sched.automation_phase = "infrastructure"
        sched.human_description = "Create EC2 for docker_host"
        sched.on_success = [ "build" ]
        self.add_schedule()

        sched = self.new_schedule()
        sched.job = "build"
        sched.archive.timeout = 3600
        sched.archive.timewait = 120
        sched.automation_phase = "infrastructure"
        sched.human_description = "Build and push container"
        self.add_schedule()

        return self.get_schedules()
