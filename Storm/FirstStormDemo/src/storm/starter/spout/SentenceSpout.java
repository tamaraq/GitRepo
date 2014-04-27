package storm.starter.spout;

import java.util.Map;
import java.util.Random;

import backtype.storm.spout.SpoutOutputCollector;
import backtype.storm.task.TopologyContext;
import backtype.storm.topology.OutputFieldsDeclarer;
import backtype.storm.topology.base.BaseRichSpout;
import backtype.storm.tuple.Fields;
import backtype.storm.tuple.Values;

public class SentenceSpout extends BaseRichSpout{
	private SpoutOutputCollector collector;
	private Random random;
	private static String[] sentences = {"wst:hello","hxl:world","xsl:good","gxx:better","wdc:best","wht:stupid","dabing:bblabla"};

	@Override
	public void open(Map conf, TopologyContext context,
			SpoutOutputCollector collector) {
		// TODO Auto-generated method stub
		this.collector = collector;
		random = new Random();
	}

	@Override
	public void nextTuple() {
		// TODO Auto-generated method stub
		String toSay = sentences[random.nextInt(sentences.length)];
		this.collector.emit(new Values(toSay));
	}

	@Override
	public void declareOutputFields(OutputFieldsDeclarer declarer) {
		// TODO Auto-generated method stub
		declarer.declare(new Fields("sentence"));
	}

}