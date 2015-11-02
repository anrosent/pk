import logging
from iptc import Chain, Rule, Table

logger = logging.getLogger(__name__)

class IptablesFirewall:
    
    rules = {}

    def unblock(self, port):
        if port in self.rules:
            logger.info("Deleting iptables rule to DROP TCP:%s" % port)        
            chain, rule = self.rules[port]
            chain.delete_rule(rule)
            del self.rules[port]
            logger.info("DROP TCP:%s iptables rule successfully deleted" % port)
        else:
            logger.info("Svc port %s is already open" % port)

    def block(self, port):
        logger.info("Creating iptables rule to DROP TCP:%s" % port)
        chain, rule = self._build_iptables_rule(port)

        logger.info("Installing iptables rule...")
        chain.insert_rule(rule)
        logger.info("Successfully installed iptables DROP TCP:%s" % port)
        self.rules[port] = (chain, rule)

    def _build_iptables_rule(self, port):
        rule = Rule()
        
        rule.protocol = "tcp"
        match = rule.create_match("tcp")
        match.dport = str(port)

        target = rule.create_target("DROP")

        chain = Chain(Table(Table.FILTER), "INPUT")
        return chain, rule

class DummyFirewall:

    def unblock(self, *args, **kwargs):
        pass

    def block(self, *args, **kwargs):
        pass
