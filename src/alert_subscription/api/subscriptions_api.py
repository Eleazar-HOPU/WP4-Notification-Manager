from apiflask import output, APIBlueprint
from flask import Blueprint, request, jsonify
from loguru import logger

from src.alert_subscription.controller.subscriptions_controller import SubscriptionsController
from src.alert_subscription.models.AlertsSwaggerModelScheme import SubscriptionList, Subscription

blueprint = APIBlueprint('subscriptions', __name__, url_prefix='/api/v1/')
# noinspection PyTypeChecker
__controller: SubscriptionsController = None


def config(controller: SubscriptionsController):
    global __controller
    __controller = controller


@blueprint.route('/notify', methods=['POST'])
def notify():
    if not request.json:
        return jsonify({'error': 'Empty body'}), 400

    category = request.json.get('category')

    __controller.search_users_by_subscription(category, message=request.json)

    return jsonify(), 200


@output(SubscriptionList)
@blueprint.route('/users/subscriptions', methods=['GET'])
def get_users():
    result = __controller.retrieve_all()

    return jsonify(result), 200


#TODO Keep Going here
@output(Subscription)
@input()
@blueprint.route('/users/<user_id>/subscriptions', methods=['POST'])
def post_subscriptions(user_id: str):
    if not request.json:
        return jsonify({'error': 'Empty body'}), 400

    result = __controller.create_subscription(user_id, request.json)

    if result is False:
        return jsonify({'error': 'Incomplete body'}), 400

    if result is None:
        return jsonify({'error': 'Already exists subscription to category'}), 400

    return jsonify(result.to_json()), 200


@output(Subscription)
@blueprint.route('/users/<user_id>/subscriptions', defaults={"subscription_id": None}, methods=['GET'])
@blueprint.route('/users/<user_id>/subscriptions/<subscription_id>', methods=['GET'])
def get_subscriptions(user_id: str, subscription_id: str):
    result = __controller.retrieve_subscription(user_id, subscription_id)

    if result is None:
        return jsonify({'error': 'Not found'}), 404

    if not subscription_id:
        return jsonify([s.to_json() for s in result]), 200

    return jsonify(result.to_json()), 200


# @api.route('/users/<user_id>/subscriptions/<subscription_id>', methods=['PUT'])
# def put_subscription(user_id: str, subscription_id: str):
#     if not request.json:
#         return jsonify({'error': 'Empty body'}), 400
#
#     result = __controller.update_subscription(user_id, subscription_id, request.json)
#
#     if result is None:
#         return jsonify({'error': 'This subscription already exists, consider deleting it'}), 400
#
#     if result == -1:
#         return jsonify({'error': 'Not found'}), 400
#
#     return jsonify(result.to_json()), 200

@output(Subscription)
@blueprint.route('/users/<user_id>/subscriptions/<subscription_id>', methods=['DELETE'])
def delete_subscription(user_id: str, subscription_id: str):

    result = __controller.delete_subscription(user_id, subscription_id)

    if result is None:
        return jsonify({'error': 'Not found'}), 400

    return jsonify(result.to_json()), 200


@output(Subscription)
@blueprint.route('/users/<user_id>/subscriptions/<subscription_id>/activate', methods=['POST'])
@blueprint.route('/users/<user_id>/subscriptions/<subscription_id>/deactivate', methods=['POST'])
def status_subscription(user_id: str, subscription_id: str):
    activated = request.path.split('/')[-1] == 'activate'

    result = __controller.switch_status_subscription(user_id, subscription_id, activated)

    if result is None:
        return jsonify({'error': 'Not found'}), 400

    return jsonify(result.to_json()), 200
