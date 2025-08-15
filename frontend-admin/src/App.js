import React, { useEffect, useState } from "react";
import {
  Card, Row, Col, List, Button, Modal, Form, Input, Upload, message
} from "antd";
import { UploadOutlined } from "@ant-design/icons";
import {
  listPeople, addPerson, deletePerson,
  listCameras, addCamera, deleteCamera
} from "./api";

export default function App() {
  const [people, setPeople] = useState([]);
  const [cameras, setCameras] = useState([]);
  const [showPerson, setShowPerson] = useState(false);
  const [showCamera, setShowCamera] = useState(false);

  const [formPerson] = Form.useForm();
  const [formCamera] = Form.useForm();

  useEffect(() => { fetchAll(); }, []);

  async function fetchAll() {
    try {
      const [pRes, cRes] = await Promise.all([listPeople(), listCameras()]);
      setPeople(pRes.data || []);
      setCameras(cRes.data || []);
    } catch {
      message.error("Failed to fetch data");
    }
  }

  async function handleAddPerson(values) {
    const { name, file } = values;
    if (!file || file.fileList.length === 0) {
      return message.error("Pick an image");
    }
    const picked = file.file.originFileObj || file.file;
    const fd = new FormData();
    fd.append("name", name);
    fd.append("image", picked);
    await addPerson(fd);
    message.success("Person added");
    setShowPerson(false);
    formPerson.resetFields();
    fetchAll();
  }

  async function handleDeletePerson(id) {
    await deletePerson(id);
    message.success("Person deleted");
    fetchAll();
  }

  async function handleAddCamera(values) {
    await addCamera({ name: values.name, rtsp_url: values.url });
    message.success("Camera added");
    setShowCamera(false);
    formCamera.resetFields();
    fetchAll();
  }

  async function handleDeleteCamera(id) {
    await deleteCamera(id);
    message.success("Camera deleted");
    fetchAll();
  }

  return (
    <div style={{ padding: 20 }}>
      <Row gutter={16}>
        <Col span={12}>
          <Card title="People" extra={<Button onClick={() => setShowPerson(true)}>Add Person</Button>}>
            <List
              dataSource={people}
              renderItem={(item) => (
                <List.Item actions={[<Button danger onClick={() => handleDeletePerson(item.id)}>Delete</Button>]}>
                  <div>
                    <b>ID:</b> {item.id} <br />
                    <b>Name:</b> {item.name} <br />
                    {item.image_url && (
                      <img src={item.image_url} alt={item.name} style={{ width: 100, height: 100, objectFit: "cover", marginTop: 5 }} />
                    )}
                  </div>
                </List.Item>
              )}
            />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="Cameras" extra={<Button onClick={() => setShowCamera(true)}>Add Camera</Button>}>
            <List
              dataSource={cameras}
              renderItem={(item) => (
                <List.Item actions={[<Button danger onClick={() => handleDeleteCamera(item.id)}>Delete</Button>]}>
                  <div>
                    <b>ID:</b> {item.id} <br />
                    <b>Name:</b> {item.name} <br />
                    <b>URL:</b> {item.rtsp_url}
                  </div>
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>

      <Modal title="Add Person" open={showPerson} onCancel={() => setShowPerson(false)} onOk={() => formPerson.submit()}>
        <Form form={formPerson} onFinish={handleAddPerson} layout="vertical">
          <Form.Item name="name" label="Name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="file" label="Image" valuePropName="file">
            <Upload beforeUpload={() => false} maxCount={1}>
              <Button icon={<UploadOutlined />}>Pick Image</Button>
            </Upload>
          </Form.Item>
        </Form>
      </Modal>

      <Modal title="Add Camera" open={showCamera} onCancel={() => setShowCamera(false)} onOk={() => formCamera.submit()}>
        <Form form={formCamera} onFinish={handleAddCamera} layout="vertical">
          <Form.Item name="name" label="Name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="url" label="RTSP URL" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
