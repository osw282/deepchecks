# ----------------------------------------------------------------------------
# Copyright (C) 2021 Deepchecks (https://www.deepchecks.com)
#
# This file is part of Deepchecks.
# Deepchecks is distributed under the terms of the GNU Affero General
# Public License (version 3 or later).
# You should have received a copy of the GNU Affero General Public License
# along with Deepchecks.  If not, see <http://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------------
#
"""Test functions of the heatmap comparison check."""
from hamcrest import assert_that, calling, close_to, greater_than, has_length, raises

from deepchecks.core.errors import DeepchecksNotSupportedError, DeepchecksValueError
from deepchecks.vision.checks import HeatmapComparison


def test_object_detection(coco_train_visiondata, coco_test_visiondata, device):
    # Arrange
    check = HeatmapComparison()

    # Act
    result = check.run(coco_train_visiondata, coco_test_visiondata, device=device)

    # Assert
    brightness_diff = result.value["diff"]
    assert_that(brightness_diff.mean(), close_to(10.420, 0.001))
    assert_that(brightness_diff.max(), close_to(45, 0.001))

    bbox_diff = result.value["diff_bbox"]
    assert_that(bbox_diff.mean(), close_to(5.589, 0.001))
    assert_that(bbox_diff.max(), close_to(24, 0.001))


def test_classification(mnist_dataset_train, mnist_dataset_test, device):
    # Arrange
    check = HeatmapComparison()

    # Act
    result = check.run(mnist_dataset_train, mnist_dataset_test, device=device, n_samples=None)

    # Assert
    brightness_diff = result.value["diff"]
    assert_that(brightness_diff.mean(), close_to(1.095, 0.001))
    assert_that(brightness_diff.max(), close_to(9, 0.001))
    assert_that(result.display, has_length(greater_than(0)))


def test_classification_without_display(mnist_dataset_train, mnist_dataset_test, device):
    # Arrange
    check = HeatmapComparison()

    # Act
    result = check.run(mnist_dataset_train, mnist_dataset_test,
                       device=device, n_samples=None, with_display=False)

    # Assert
    brightness_diff = result.value["diff"]
    assert_that(brightness_diff.mean(), close_to(1.095, 0.001))
    assert_that(brightness_diff.max(), close_to(9, 0.001))
    assert_that(result.display, has_length(0))


def test_classification_limit_classes(mnist_dataset_train, mnist_dataset_test, device):
    # Arrange
    check = HeatmapComparison(classes_to_display=['9'])

    # Act
    result = check.run(mnist_dataset_train, mnist_dataset_test, device=device, n_samples=None)

    # Assert
    brightness_diff = result.value["diff"]
    assert_that(brightness_diff.mean(), close_to(2.149, 0.001))
    assert_that(brightness_diff.max(), close_to(21, 0.001))


def test_object_detection_limit_classes(coco_train_visiondata, coco_test_visiondata, device):
    # Arrange
    check = HeatmapComparison(classes_to_display=['bicycle', 'bench'])

    # Act
    result = check.run(coco_train_visiondata, coco_test_visiondata, device=device)

    # Assert
    brightness_diff = result.value["diff"]
    assert_that(brightness_diff.mean(), close_to(39.458, 0.001))
    assert_that(brightness_diff.max(), close_to(170, 0.001))

    bbox_diff = result.value["diff_bbox"]
    assert_that(bbox_diff.mean(), close_to(15.154, 0.001))
    assert_that(bbox_diff.max(), close_to(75, 0.001))


def test_limit_classes_nonexistant_class(coco_train_visiondata, coco_test_visiondata, device):
    # Arrange
    check = HeatmapComparison(classes_to_display=['1000'])

    # Act & Assert
    assert_that(
        calling(check.run).with_args(coco_train_visiondata, coco_test_visiondata, device=device),
        raises(DeepchecksValueError,
               r'Provided list of class ids to display \[\'1000\'\] not found in training dataset.')
    )


def test_custom_task(mnist_train_custom_task, mnist_test_custom_task, device):
    # Arrange
    check = HeatmapComparison()

    # Act
    result = check.run(mnist_train_custom_task, mnist_test_custom_task, device=device, n_samples=None)

    # Assert
    brightness_diff = result.value["diff"]
    assert_that(brightness_diff.mean(), close_to(1.095, 0.001))
    assert_that(brightness_diff.max(), close_to(9, 0.001))


def test_dataset_name(mnist_dataset_train, mnist_dataset_test, device):
    mnist_dataset_train.name = 'Ref'
    mnist_dataset_test.name = 'Win'

    result = HeatmapComparison().run(mnist_dataset_train, mnist_dataset_test, device=device)

    assert_that(result.display[0].layout.annotations[0].text, 'Ref')
    assert_that(result.display[0].layout.annotations[1].text, 'Win')