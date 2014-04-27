package storm.starter;

import storm.starter.bolt.SentenceAnalyzeBolt;
import storm.starter.bolt.SentencePrintBolt;
import storm.starter.spout.SentenceSpout;
import backtype.storm.Config;
import backtype.storm.LocalCluster;
import backtype.storm.topology.TopologyBuilder;
import backtype.storm.utils.Utils;

public class SentenceTopology {
	public static void main(String[] args){
		try{
			TopologyBuilder builder = new TopologyBuilder();
			
			builder.setSpout("spout", new SentenceSpout());
			builder.setBolt("analyze", new SentenceAnalyzeBolt()).shuffleGrouping("spout");
			builder.setBolt("print", new SentencePrintBolt()).shuffleGrouping("analyze");
			
			Config conf = new Config();
			conf.setDebug(true);
			
			LocalCluster cluster = new LocalCluster();
			
			cluster.submitTopology("test", conf, builder.createTopology());
			
			Utils.sleep(10000);
			
			cluster.killTopology("test");
			cluster.shutdown();
			
		}catch(Exception e){
			System.err.println(e.getMessage());
		}
	}
}