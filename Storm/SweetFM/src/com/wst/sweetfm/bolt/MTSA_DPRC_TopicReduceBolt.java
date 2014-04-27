/**
 * MTSA_DPRC_ReduceBolt.java
 * 版权所有(C) 2014 
 * 创建:wwssttt 2014-03-08 20:29:00
 * 描述:接收上游计算结果并组装成新的概率分布
 */
package com.wst.sweetfm.bolt;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.Map;
import java.util.Iterator;
import java.util.Map.Entry;
import java.util.Queue;

import org.json.simple.JSONObject;

import com.wst.sweetfm.util.MTSA_Const;
import com.wst.sweetfm.util.SongTopicReader;

import backtype.storm.topology.BasicOutputCollector;
import backtype.storm.topology.OutputFieldsDeclarer;
import backtype.storm.topology.base.BaseBasicBolt;
import backtype.storm.tuple.Fields;
import backtype.storm.tuple.Tuple;
import backtype.storm.tuple.Values;

public class MTSA_DPRC_TopicReduceBolt extends BaseBasicBolt{
	
	private StringBuffer _topicBuffer = new StringBuffer();
	private ArrayList<Integer> _topicList = new ArrayList<Integer>();
	Queue<String> _queue = new LinkedList<String>();
	@Override
    public void execute(Tuple tuple, BasicOutputCollector collector) {
	  //System.err.println("TopicReduceBolt:"+this.topicBuffer.toString());
      //String input = tuple.getString(1);
      //collector.emit(new Values(tuple.getValue(0), input + "!"));
      String nextStr = tuple.getString(1);
      String[] items = nextStr.split(":");
      Integer topicId = Integer.valueOf(items[0]);
      if(!_topicList.contains(topicId)){
    	  _topicList.add(topicId);
    	  _topicBuffer.append(nextStr);
    	  _topicBuffer.append("#");
      }
	  
	  if(_topicList.size() == MTSA_Const.TOPIC_NUM){
		  _topicBuffer.deleteCharAt(_topicBuffer.length()-1);
		  //collector.emit(new Values(tuple.getValue(0),this.topicBuffer.toString()));
		  _topicBuffer.append(";");
		  
		  HashMap<Integer,HashMap<Integer,Double>> songMap = SongTopicReader.getSongMap();
		  System.err.println("reader count = "+SongTopicReader.count);
		  Iterator<Entry<Integer, HashMap<Integer, Double>>> iter = songMap.entrySet().iterator();
		  
		  while(iter.hasNext()){
			  Map.Entry<Integer, HashMap<Integer, Double>> entry = (Map.Entry<Integer, HashMap<Integer, Double>>) iter.next();
			  Integer sid = (Integer) entry.getKey();
			  HashMap<Integer,Double> topicMap = (HashMap<Integer, Double>) entry.getValue(); 
			  StringBuffer sb = new StringBuffer();
			  sb.append(sid);
			  sb.append(">");
			  Iterator<Entry<Integer, Double>> topicIter = topicMap.entrySet().iterator();
			  while(topicIter.hasNext()){
				  Map.Entry<Integer, Double> topicEntry = (Map.Entry<Integer, Double>) topicIter.next();
				  Integer tid = (Integer) topicEntry.getKey();
				  Double probability = (Double) topicEntry.getValue();
				  sb.append(tid);
				  sb.append(":");
				  sb.append(probability);
				  sb.append("#");
			  }
			  sb.deleteCharAt(sb.length()-1);
			  _queue.add(sb.toString());
		  }
		  
		  while(!_queue.isEmpty()){
			  String resultStr = _queue.poll();
			  collector.emit(new Values(tuple.getValue(0),_topicBuffer.toString()+resultStr));
		  }
	  }
    }
	  

    @Override
    public void declareOutputFields(OutputFieldsDeclarer declarer) {
      declarer.declare(new Fields("id", "song_distribution"));
    }
}