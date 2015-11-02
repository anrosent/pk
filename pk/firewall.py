import logging
import iptc
from iptc import Chain, Rule, Table

logger = logging.getLogger(__name__)

class IptablesFirewall:
    
    rules = {}

    def unblock(self, port, client):
        logger.info("Unblocking port %s for client %s" % (port, client))
        if not self._rule_exists(port, client):
            chain, rule = self._build_iptables_accept_rule(port, client)
            chain.insert_rule(rule)
            self._put_rule(port, client, chain, rule)
            logger.info("DROP TCP:%s iptables rule successfully deleted for client %s" % (port, client))
        else:
            logger.info("Svc port %s is already open for client %s" % (port, client))

    def block_all(self, port):
        logger.info("Creating iptables rule to DROP TCP:%s for all clients" % (port))
        chain, rule = self._build_iptables_drop_rule(port)

        logger.info("Installing iptables rule...")
        chain.insert_rule(rule)
        logger.info("Successfully installed iptables DROP TCP:%s for all clients" % (port))
        self._put_rule(port, None, chain, rule)


    def clear(self):
        for (port, client) in self.rules:
            self._delete_rule(port, client)
        self.rules = {}
    
    ########################################

    def _build_iptables_drop_rule(self, port):
        rule = Rule()
        
        rule.protocol = "tcp"
        match = rule.create_match("tcp")
        match.dport = str(port)

        target = rule.create_target("DROP")

        chain = Chain(Table(Table.FILTER), "INPUT")
        return chain, rule
   
    def _build_iptables_accept_rule(self, port, client):
        src, src_port = client

        rule = Rule()
        rule.protocol = "tcp"
        rule.src = src
        match = rule.create_match("tcp")
        match.dport = str(port)
        match.sport = str(src_port)

        target = rule.create_target("ACCEPT")
        chain = Chain(Table(Table.FILTER), "INPUT")
        return chain, rule

    def _rule_exists(self, port, client):
        return (port, client) in self.rules

    def _delete_rule(self, port, client):
        logger.info("Deleting iptables rule to DROP TCP:%s for client %s" % (port, client))
        chain, rule = self._get_rule(port, client)
        try:
            chain.delete_rule(rule)
        except iptc.ip4tc.IPTCError as e:
            logger.error("Error deleting iptables rule: %s" % str(e))

    def _get_rule(self, port, client):
        return self.rules[(port, client)]

    def _put_rule(self, port, client, chain, rule):
        self.rules[(port, client)] = (chain, rule)



class DummyFirewall:

    def unblock(self, *args, **kwargs):
        pass

    def block(self, *args, **kwargs):
        pass

    def clear(self):
        pass

    def block_all(self, *args, **kwargs):
        pass
