import classNames from 'classnames';
import Link from 'next/link';
import { Card, Icon, Image, Label, Segment } from 'semantic-ui-react';

import t from '../../misc/lang';
import { FieldPath, ServerArtist } from '../../misc/types';
import { urlstring } from '../../misc/utility';
import Rating from '../Rating';

export type ArtistCardLabelData = DeepPick<
  ServerArtist,
  | 'id'
  | 'info'
  | 'preferred_name.name'
  | 'metatags.favorite'
  | 'metatags.follow'
  | 'circles.[].id'
  | 'circles.[].name'
>;

export const artistCardLabelDataFields: FieldPath<ServerArtist>[] = [
  'info',
  'preferred_name.name',
  'metatags.favorite',
  'metatags.follow',
  'circles.id',
  'circles.name',
];

export default function ArtistCardLabel({
  data,
  ...props
}: {
  data: ArtistCardLabelData;
} & React.ComponentProps<typeof Card>) {
  return (
    <Card
      {...props}
      as={Segment}
      size="tiny"
      color="blue"
      className={classNames('default-card', props.className)}>
      <Card.Content>
        <Image
          floated="left"
          size="mini"
          circular
          src="/img/default.png"
          alt="default"
        />
        <Card.Header>
          {data?.preferred_name?.name}
          <Label size="mini" className="right">
            {t`ID`}
            <Label.Detail>{data.id}</Label.Detail>
          </Label>
          <Rating
            icon="thumbtack"
            size="big"
            title={t`Follow status`}
            color="blue"
            className="right"
            defaultRating={data?.metatags?.follow ? 1 : 0}
          />
          <Rating
            icon="heart"
            size="big"
            color="red"
            className="right"
            defaultRating={data?.metatags?.favorite ? 1 : 0}
          />
        </Card.Header>
        <Card.Meta>
          <Label.Group size="small">
            {data?.circles?.map?.((c) => (
              <Label color="teal" key={c?.id}>
                <Icon name="group" /> {c.name}
              </Label>
            ))}
          </Label.Group>
        </Card.Meta>
        <Card.Meta>{data.info || t`No description`}</Card.Meta>
        <Card.Meta className="clearfix">
          <Link
            href={urlstring('/library', {
              q: `artist:"${data.preferred_name.name}"`,
            })}
            passHref>
            <Label
              size="small"
              empty
              className="right"
              icon="grid layout"
              title={t`Show galleries`}
              as="a"
            />
          </Link>
        </Card.Meta>
      </Card.Content>
    </Card>
  );
}