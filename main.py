from model import AppModel
from view import AppView
import streamlit as st
from controller import AppController
if __name__ == "__main__":
    # Create instances of Model, View, and Controller
    model = AppModel()
    view = AppView()
    controller = AppController(model, view)
    view.set_controller(controller)
    #model.show_artikel()

    # Run the application
    view.run()