from pyflink.common import SimpleStringSchema
from pyflink.common import Time
from pyflink.common.typeinfo import Types, RowTypeInfo
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.datastream import StreamExecutionEnvironment, TimeCharacteristic
from pyflink.datastream.connectors import DeliveryGuarantee
from pyflink.datastream.connectors.kafka import KafkaSource, \
    KafkaOffsetsInitializer, KafkaSink, KafkaRecordSerializationSchema
from pyflink.datastream.formats.json import JsonRowDeserializationSchema
from pyflink.datastream.functions import MapFunction
from pyflink.datastream.functions import ReduceFunction
from pyflink.common.types import Row
from pyflink.datastream.window import TumblingProcessingTimeWindows


class MinimalTemperature(ReduceFunction):
    def reduce(self, value_1: Row, value_2: Row):
        if value_1.temperature < value_2.temperature:
            return value_1
        else:
            return value_2

class TemperatureConverter(MapFunction):
    def map(self, data_entry):
        device_id, temperature, execution_time = data_entry
        temperature_celsius = temperature - 273
        converted_data = {
            "device_id": device_id,
            "temperature_celsius": temperature_celsius,
            "execution_time": execution_time,
        }
        return str(converted_data)

def python_data_stream_example():
    env = StreamExecutionEnvironment.get_execution_environment()
    # Set the parallelism to be one to make sure that all data including fired timer and normal data
    # are processed by the same worker and the collected result would be in order which is good for
    # assertion.
    env.set_parallelism(1)
    env.set_stream_time_characteristic(TimeCharacteristic.EventTime)
    env.enable_checkpointing(3000)
    env.get_checkpoint_config().set_checkpoint_interval(3000)
    env.get_checkpoint_config().set_checkpoint_storage_dir("file:///opt/pyflink/tmp/checkpoints/logs")

    type_info: RowTypeInfo = Types.ROW_NAMED(['device_id', 'temperature', 'execution_time'],
                                             [Types.LONG(), Types.DOUBLE(), Types.INT()])

    json_row_schema = JsonRowDeserializationSchema.builder().type_info(type_info).build()

    source = KafkaSource.builder() \
        .set_bootstrap_servers('kafka:9092') \
        .set_topics('itmo2023') \
        .set_group_id('pyflink-e2e-source') \
        .set_starting_offsets(KafkaOffsetsInitializer.earliest()) \
        .set_value_only_deserializer(json_row_schema) \
        .build()

    sink = KafkaSink.builder() \
        .set_bootstrap_servers('kafka:9092') \
        .set_record_serializer(KafkaRecordSerializationSchema.builder()
                               .set_topic('itmo2023_processed')
                               .set_value_serialization_schema(SimpleStringSchema())
                               .build()
                               ) \
        .set_delivery_guarantee(DeliveryGuarantee.AT_LEAST_ONCE) \
        .build()
    

    ds = env.from_source(source, WatermarkStrategy.no_watermarks(), "Kafka Source")
    grouped_stream = ds.key_by(lambda x: x[0])
    windowed_stream = grouped_stream.window(TumblingProcessingTimeWindows.of(Time.seconds(5)))
    reduced_stream = windowed_stream.reduce(MinimalTemperature())
    mapped_stream = reduced_stream.map(TemperatureConverter(), Types.STRING())
    mapped_stream.sink_to(sink)
    env.execute_async("Tumbling preprocess")
 
if __name__ == "__main__":
    python_data_stream_example()